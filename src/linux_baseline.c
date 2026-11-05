#define _GNU_SOURCE
#include <errno.h>
#include <math.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/utsname.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define MAX_WORKERS 8
#define MAX_SAMPLES 2000

static pid_t children[MAX_WORKERS];
static int child_count;

static void cleanup(void)
{
    for (int i = 0; i < child_count; ++i) {
        if (children[i] <= 0) continue;
        kill(children[i], SIGTERM);
        while (waitpid(children[i], NULL, 0) < 0 && errno == EINTR) {}
    }
}

static void fail(const char *message)
{
    fprintf(stderr, "linux_baseline: %s (%s)\n", message, strerror(errno));
    exit(EXIT_FAILURE);
}

static int number(const char *text, int low, int high)
{
    char *end;
    errno = 0;
    long n = strtol(text, &end, 10);
    if (errno || !*text || *end || n < low || n > high) {
        fprintf(stderr, "linux_baseline: invalid argument: %s\n", text);
        exit(EXIT_FAILURE);
    }
    return (int)n;
}

static int64_t ns(clockid_t clock)
{
    struct timespec t;
    if (clock_gettime(clock, &t)) fail("clock_gettime");
    return (int64_t)t.tv_sec * 1000000000 + t.tv_nsec;
}

/* Burn an actual process-CPU-time budget, independent of CPU frequency. */
static double burn(int microseconds)
{
    int64_t start = ns(CLOCK_PROCESS_CPUTIME_ID), end;
    volatile unsigned long state = 1;
    do {
        for (int j = 0; j < 256; ++j) state = state * 1664525UL + 1013904223UL;
        end = ns(CLOCK_PROCESS_CPUTIME_ID);
    } while (end - start < (int64_t)microseconds * 1000);
    return (end - start) / 1e6;
}

static void transfer(int fd, void *buffer, size_t size, int writing)
{
    char *p = buffer;
    while (size) {
        ssize_t n = writing ? write(fd, p, size) : read(fd, p, size);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) fail("pipe transfer failed");
        size -= (size_t)n;
        p += n;
    }
}

static int compare(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

typedef struct { int id; double wall_ms, cpu_ms; } Worker;

int main(int argc, char **argv)
{
    int workers = 2, samples = 40, period_ms = 20, burst_us = 500, worker_ms = 800;
    for (int i = 1; i < argc; ++i) {
        const char *key = argv[i];
        if (i + 1 >= argc) { errno = EINVAL; fail("missing option value"); }
        const char *v = argv[++i];
        if (!strcmp(key, "--workers")) workers = number(v, 0, MAX_WORKERS);
        else if (!strcmp(key, "--samples")) samples = number(v, 1, MAX_SAMPLES);
        else if (!strcmp(key, "--period-ms")) period_ms = number(v, 1, 1000);
        else if (!strcmp(key, "--burst-us")) burst_us = number(v, 1, 100000);
        else if (!strcmp(key, "--worker-ms")) worker_ms = number(v, 1, 60000);
        else { errno = EINVAL; fail("unknown option"); }
    }
    cpu_set_t allowed, chosen;
    if (sched_getaffinity(0, sizeof allowed, &allowed)) fail("get affinity");
    int cpu = -1;
    for (int i = 0; i < CPU_SETSIZE; ++i)
        if (CPU_ISSET(i, &allowed)) { cpu = i; break; }
    if (cpu < 0) { errno = EINVAL; fail("no allowed CPU"); }
    CPU_ZERO(&chosen);
    CPU_SET(cpu, &chosen);
    if (sched_setaffinity(0, sizeof chosen, &chosen)) fail("pin CPU");
    int scheduler = sched_getscheduler(0);
    if (scheduler < 0) fail("read scheduler policy");
    if (scheduler != SCHED_OTHER) {
        errno = EINVAL;
        fail("baseline requires the ordinary SCHED_OTHER policy");
    }
    int gate[2], output[2];
    if (pipe(gate) || pipe(output)) fail("pipe");
    if (atexit(cleanup)) { errno = ENOMEM; fail("register cleanup"); }
    for (int i = 0; i < workers; ++i) {
        pid_t pid = fork();
        if (pid < 0) fail("fork");
        if (pid == 0) {
            child_count = 0;
            close(gate[1]); close(output[0]);
            char token;
            transfer(gate[0], &token, 1, 0);
            close(gate[0]);
            Worker w = {.id = i};
            int64_t begin = ns(CLOCK_MONOTONIC);
            w.cpu_ms = burn(worker_ms * 1000);
            w.wall_ms = (ns(CLOCK_MONOTONIC) - begin) / 1e6;
            /* Each fixed-size record is smaller than PIPE_BUF: atomic write. */
            transfer(output[1], &w, sizeof w, 1);
            close(output[1]);
            _exit(EXIT_SUCCESS);
        }
        children[child_count++] = pid;
    }
    close(gate[0]); close(output[1]);
    for (int i = 0; i < workers; ++i) {
        char token = 'x';
        transfer(gate[1], &token, 1, 1);
    }
    close(gate[1]);
    double wake[MAX_SAMPLES], response[MAX_SAMPLES], cpu_used[MAX_SAMPLES];
    int64_t epoch = ns(CLOCK_MONOTONIC) + 20000000;
    for (int i = 0; i < samples; ++i) {
        int64_t release = epoch + (int64_t)i * period_ms * 1000000;
        struct timespec deadline = {.tv_sec = release / 1000000000,
                                    .tv_nsec = release % 1000000000};
        int error;
        do { error = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &deadline, NULL); }
        while (error == EINTR);
        if (error) { errno = error; fail("absolute sleep"); }
        wake[i] = (ns(CLOCK_MONOTONIC) - release) / 1e6;
        cpu_used[i] = burn(burst_us);
        response[i] = (ns(CLOCK_MONOTONIC) - release) / 1e6;
    }
    Worker worker_results[MAX_WORKERS];
    for (int i = 0; i < workers; ++i) {
        int status;
        pid_t waited;
        do { waited = waitpid(children[i], &status, 0); } while (waited < 0 && errno == EINTR);
        if (waited < 0) fail("waitpid");
        children[i] = 0;
        if (!WIFEXITED(status) || WEXITSTATUS(status)) {
            errno = ECHILD; fail("background worker failed");
        }
    }
    for (int i = 0; i < workers; ++i) {
        Worker w;
        transfer(output[0], &w, sizeof w, 0);
        if (w.id < 0 || w.id >= workers) { errno = EINVAL; fail("invalid worker result"); }
        worker_results[w.id] = w;
    }
    close(output[0]);
    struct utsname system;
    if (uname(&system)) fail("uname");
    double sorted[MAX_SAMPLES], total = 0;
    for (int i = 0; i < samples; ++i) { sorted[i] = wake[i]; total += wake[i]; }
    qsort(sorted, (size_t)samples, sizeof sorted[0], compare);
    /* Nearest-rank percentiles; include their exact definition in the report. */
    int p50 = (samples * 50 + 99) / 100 - 1;
    int p95 = (samples * 95 + 99) / 100 - 1;
    printf("{\"kind\":\"linux_baseline\",\"kernel\":\"%s\",\"cpu\":%d,"
           "\"scheduler\":\"SCHED_OTHER\",\"workers\":%d,\"sample_count\":%d,"
           "\"period_ms\":%d,\"burst_us\":%d,\"worker_cpu_budget_ms\":%d,"
           "\"wake_mean_ms\":%.6f,\"wake_p50_ms\":%.6f,\"wake_p95_ms\":%.6f,"
           "\"wake_max_ms\":%.6f,\"samples\":[\n",
           system.release, cpu, workers, samples, period_ms, burst_us, worker_ms,
           total / samples, sorted[p50], sorted[p95], sorted[samples - 1]);
    for (int i = 0; i < samples; ++i)
        printf("%s{\"index\":%d,\"release_offset_ms\":%d,\"wake_lateness_ms\":%.6f,"
               "\"completion_latency_ms\":%.6f,\"cpu_ms\":%.6f}", i ? ",\n" : "",
               i, i * period_ms, wake[i], response[i], cpu_used[i]);
    printf("\n],\"background\":[");
    for (int i = 0; i < workers; ++i)
        printf("%s{\"id\":%d,\"wall_ms\":%.6f,\"cpu_ms\":%.6f}", i ? "," : "",
               i, worker_results[i].wall_ms, worker_results[i].cpu_ms);
    puts("]}");
    return EXIT_SUCCESS;
}
