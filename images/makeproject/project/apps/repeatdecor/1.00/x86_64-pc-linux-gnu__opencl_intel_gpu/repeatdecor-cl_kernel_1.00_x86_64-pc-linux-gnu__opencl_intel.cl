#ifdef BOINC
const int RUNS_PER_CHECKPOINT = 16;
#endif

// Constants
__constant ulong XL = 0x9E3779B97F4A7C15UL;
__constant ulong XH = 0x6A09E667F3BCC909UL;
__constant ulong XL_BASE = XL * 4; // HASH_BATCH_SIZE = 4
__constant int HASH_BATCH_SIZE = 4;
__constant int SCORE_CUTOFF = 50;

// Structs
typedef struct {
    long  score;
    ulong seed;
    long  a, b;
} Result;

// Utility functions
inline ulong rotl64(ulong x, uint r) {
    return (x << r) | (x >> (64u - r));
}

inline ulong mix64(ulong z) {
    const ulong M1 = 0xBF58476D1CE4E5B9UL;
    const ulong M2 = 0x94D049BB133111EBUL;
    z = (z ^ (z >> 30)) * M1;
    z = (z ^ (z >> 27)) * M2;
    return z ^ (z >> 31);
}

// Fixed ffsll implementation using clz
inline int ffsll(ulong x) {
    if (x == 0) return 0;
    return 64 - clz(x & -x);
}

// PRNG128 implementation
typedef struct {
    ulong lo;
    ulong hi;
} PRNG128;

inline void PRNG128_init(PRNG128 *rng, ulong s) {
    rng->lo = mix64(s);
    rng->hi = mix64(s + XL);
}

inline void PRNG128_init2(PRNG128 *rng, ulong _lo, ulong _hi) {
    rng->lo = _lo;
    rng->hi = _hi;
}

inline ulong PRNG128_next64(PRNG128 *rng) {
    ulong res = rotl64(rng->lo + rng->hi, 17) + rng->lo;
    ulong t   = rng->hi ^ rng->lo;
    rng->lo = rotl64(rng->lo, 49) ^ t ^ (t << 21);
    rng->hi = rotl64(t, 28);
    return res;
}

inline uint PRNG128_nextLongLower32(PRNG128 *rng) {
    ulong t = rng->hi ^ rng->lo;
    rng->lo = rotl64(rng->lo, 49) ^ t ^ (t << 21);
    rng->hi = rotl64(t, 28);
    t = rng->hi ^ rng->lo;
    return (uint)((rotl64(rng->lo + rng->hi, 17) + rng->lo) >> 32);
}

inline void PRNG128_advance(PRNG128 *rng) {
    ulong t = rng->hi ^ rng->lo;
    rng->lo = rotl64(rng->lo, 49) ^ t ^ (t << 21);
    rng->hi = rotl64(t, 28);
}

inline long PRNG128_nextLong(PRNG128 *rng) {
    int high = (int)(PRNG128_next64(rng) >> 32);
    int low  = (int)(PRNG128_next64(rng) >> 32);
    return ((long)high << 32) + (long)low;
}

inline void compute_ab(ulong seed, long *a, long *b) {
    PRNG128 rng;
    PRNG128_init(&rng, seed);
    *a = PRNG128_nextLong(&rng) | 1L;
    *b = PRNG128_nextLong(&rng) | 1L;
}

// Core computation functions
inline bool goodLower32(PRNG128 *rng) {
    uint al = PRNG128_nextLongLower32(rng) | 1U;
    PRNG128_advance(rng);
    uint bl = PRNG128_nextLongLower32(rng) | 1U;

    return 
        al == bl || al + bl == 0 ||
        3*al == bl || 3*al + bl == 0 ||
        al == 3*bl || al + 3*bl == 0 ||
        5*al == bl || 5*al + bl == 0 ||
        al == 5*bl || al + 5*bl == 0 ||
        3*al == 5*bl || 3*al + 5*bl == 0 ||
        5*al == 3*bl || 5*al + 3*bl == 0 ||
        7*al == bl || 7*al + bl == 0 ||
        al == 7*bl || al + 7*bl == 0 ||
        7*al == 3*bl || 7*al + 3*bl == 0 ||
        7*al == 5*bl || 7*al + 5*bl == 0 ||
        5*al == 7*bl || 5*al + 7*bl == 0 ||
        7*al == 3*bl || 7*al + 3*bl == 0;
}

inline void processFullPrngState(ulong xseed, __global Result *results, __global volatile int *result_idx) {  
    long a, b;
    compute_ab(xseed, &a, &b);

    long score = 0;
    ulong x;
    int tz;

    x = (ulong)a ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)a ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-a) ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(3 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-3 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)a ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-a) ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(5 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-5 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(3 * a) ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-3 * a) ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(5 * a) ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-5 * a) ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)a ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-a) ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(7 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-7 * a) ^ (ulong)b;
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(3 * a) ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-3 * a) ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(7 * a) ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-7 * a) ^ (ulong)(3 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(5 * a) ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-5 * a) ^ (ulong)(7 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(7 * a) ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    x = (ulong)(-7 * a) ^ (ulong)(5 * b);
    tz = x ? (ffsll(x) - 1) : 64;
    score = tz > score ? tz : score;

    if (score < SCORE_CUTOFF)
        return;

    ulong seed = xseed ^ XH;
    int this_result_idx = atomic_add(result_idx, 1);
    
    // Assign struct fields individually (no C++ aggregate initialization)
    results[this_result_idx].score = score;
    results[this_result_idx].seed  = seed;
    results[this_result_idx].a     = a;
    results[this_result_idx].b     = b;
}

// Main kernel
__kernel void searchKernel(ulong start_seed, 
                          __global Result *results, 
                          __global volatile int *result_idx, 
                          __global volatile uint *checksum) {
    ulong gid = get_global_id(0) & 0xFFFFFFFF;
    ulong seed_base = (start_seed + gid) * XL_BASE;

    ulong hashes[HASH_BATCH_SIZE + 1];
    for (int i = 0; i <= HASH_BATCH_SIZE; i++)
        hashes[i] = mix64(seed_base + i * XL);

    for (int i = 0; i < HASH_BATCH_SIZE; i++) {
        PRNG128 prng;
        PRNG128_init2(&prng, hashes[i], hashes[i+1]);
        
        if (!goodLower32(&prng))
            continue;
            
        ulong curr_s = seed_base + i * XL;
        processFullPrngState(curr_s, results, result_idx);
        atomic_add(checksum, 1);
    }
}
