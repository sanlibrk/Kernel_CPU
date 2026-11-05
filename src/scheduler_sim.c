/* Single-CPU, integer-ms reference model. NOT a Linux scheduler.
 * Tasks have one CPU burst, no I/O; context switches have zero cost.
 * rr: FIFO round robin. interactive: limited preference + aging + RR.
 */
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TASKS 256
#define LIMIT 1000000

typedef struct {
    int id, interactive, arrival, burst, remaining, start, finish, ready_since;
    unsigned long ticket;
} Task;

static Task tasks[MAX_TASKS];
static int count;

static void fail(const char *message)
{
    fprintf(stderr, "scheduler_sim: %s\n", message);
    exit(EXIT_FAILURE);
}

static int number(const char *s, int min)
{
    char *end;
    errno = 0;
    long value = strtol(s, &end, 10);
    if (errno || *s == '\0' || *end != '\0' || value < min || value > LIMIT)
        fail("integer outside supported range");
    return (int)value;
}

static void load(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) fail("cannot open workload");
    char line[256];
    if (!fgets(line, sizeof line, f)) fail("missing CSV header");
    line[strcspn(line, "\r\n")] = '\0';
    if (strcmp(line, "id,class,arrival_ms,burst_ms")) fail("invalid CSV header");
    int total = 0;
    while (fgets(line, sizeof line, f)) {
        if (!strchr(line, '\n') && !feof(f)) fail("CSV line too long");
        line[strcspn(line, "\r\n")] = '\0';
        if (!*line) continue;
        if (count == MAX_TASKS) fail("too many tasks (maximum 256)");
        char *fields[4];
        char *p = line;
        for (int i = 0; i < 4; ++i) {
            fields[i] = p;
            char *comma = strchr(p, ',');
            if (i < 3) {
                if (!comma) fail("expected four CSV fields");
                *comma = '\0';
                p = comma + 1;
            } else if (comma) fail("expected four CSV fields");
        }
        Task *t = &tasks[count];
        t->id = number(fields[0], 1);
        if (!strcmp(fields[1], "interactive")) t->interactive = 1;
        else if (strcmp(fields[1], "background")) fail("unknown task class");
        t->arrival = number(fields[2], 0);
        t->burst = number(fields[3], 1);
        total += t->burst;
        if (total > LIMIT) fail("total CPU demand exceeds 1000000 ms");
        for (int i = 0; i < count; ++i)
            if (tasks[i].id == t->id) fail("duplicate task id");
        t->remaining = t->burst;
        t->start = -1;
        t->ready_since = t->arrival;
        ++count;
    }
    if (ferror(f)) fail("workload read failed");
    fclose(f);
    if (!count) fail("empty workload");
}

static int ready(int i, int now)
{
    return tasks[i].arrival <= now && tasks[i].remaining > 0;
}

/* New arrivals join by arrival time, then id (independent of CSV ordering). */
static void admit(int now, unsigned long *sequence)
{
    for (;;) {
        int best = -1;
        for (int i = 0; i < count; ++i) {
            Task *t = &tasks[i];
            if (!ready(i, now) || t->ticket) continue;
            if (best < 0 || t->arrival < tasks[best].arrival ||
                (t->arrival == tasks[best].arrival && t->id < tasks[best].id))
                best = i;
        }
        if (best < 0) return;
        tasks[best].ticket = ++*sequence;
    }
}

static int choose(int now, int custom, int budget, int aging)
{
    int oldest = -1, preferred = -1, fallback = -1, has_background = 0;
    for (int i = 0; i < count; ++i) {
        if (!ready(i, now)) continue;
        Task *t = &tasks[i];
        if (!t->interactive) has_background = 1;
        if (fallback < 0 || t->ticket < tasks[fallback].ticket) fallback = i;
        if (now - t->ready_since >= aging &&
            (oldest < 0 || t->ready_since < tasks[oldest].ready_since ||
             (t->ready_since == tasks[oldest].ready_since &&
              t->ticket < tasks[oldest].ticket))) oldest = i;
    }
    if (!custom) return fallback;
    /* Aging overrides preference/budget. This is not a hard latency bound. */
    if (oldest >= 0) return oldest;
    for (int i = 0; i < count; ++i) {
        if (!ready(i, now)) continue;
        int wanted = budget > 0 || !has_background;
        if (tasks[i].interactive != wanted) continue;
        if (preferred < 0 || tasks[i].ticket < tasks[preferred].ticket) preferred = i;
    }
    return preferred >= 0 ? preferred : fallback;
}

int main(int argc, char **argv)
{
    int custom = 1, quantum = 4, window = 20, limit = 8, aging = 20;
    const char *path = NULL;
    for (int i = 1; i < argc; ++i) {
        if (!strcmp(argv[i], "--policy") && i + 1 < argc) {
            const char *v = argv[++i];
            if (!strcmp(v, "rr")) custom = 0;
            else if (!strcmp(v, "interactive")) custom = 1;
            else fail("policy must be rr or interactive");
        } else if (!strcmp(argv[i], "--quantum") && i + 1 < argc)
            quantum = number(argv[++i], 1);
        else if (!strcmp(argv[i], "--window") && i + 1 < argc)
            window = number(argv[++i], 1);
        else if (!strcmp(argv[i], "--budget") && i + 1 < argc)
            limit = number(argv[++i], 1);
        else if (!strcmp(argv[i], "--aging") && i + 1 < argc)
            aging = number(argv[++i], 1);
        else if (argv[i][0] != '-' && !path) path = argv[i];
        else fail("usage: scheduler_sim [--policy rr|interactive] [--quantum N] "
                  "[--window N] [--budget N] [--aging N] workload.csv");
    }
    if (!path) fail("workload path required");
    if (limit > window) fail("budget cannot exceed window");
    load(path);
    int now = 0, done = 0, current = -1, left = 0, budget = limit;
    unsigned long sequence = 0;
    while (done < count) {
        if (now % window == 0) budget = limit;
        admit(now, &sequence);
        int background_ready = 0;
        for (int i = 0; i < count; ++i)
            if (ready(i, now) && !tasks[i].interactive) background_ready = 1;
        int budget_preempt = custom && current >= 0 &&
            tasks[current].interactive && budget == 0 && background_ready;
        if (current >= 0 && (left == 0 || budget_preempt)) {
            tasks[current].ticket = ++sequence;
            tasks[current].ready_since = now;
            current = -1;
        }
        if (current < 0) {
            current = choose(now, custom, budget, aging);
            left = quantum;
        }
        if (current < 0) { ++now; continue; }
        Task *t = &tasks[current];
        if (t->start < 0) t->start = now;
        --t->remaining;
        --left;
        if (t->interactive && budget > 0) --budget;
        ++now;
        if (!t->remaining) {
            t->finish = now;
            ++done;
            current = -1;
        }
    }
    puts("id,class,arrival_ms,burst_ms,start_ms,finish_ms,response_ms,waiting_ms,turnaround_ms");
    for (int i = 0; i < count; ++i) {
        Task *t = &tasks[i];
        int turn = t->finish - t->arrival;
        printf("%d,%s,%d,%d,%d,%d,%d,%d,%d\n", t->id,
               t->interactive ? "interactive" : "background", t->arrival,
               t->burst, t->start, t->finish, t->start - t->arrival,
               turn - t->burst, turn);
    }
    return EXIT_SUCCESS;
}
