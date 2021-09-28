Benchmark: bimodal_x.prob

The experiment is comparing sampling by simulation with sampling using the cornish-fisher expansion.

### simulation.json
Contains 100,000 samples of x at iteration 10 collected by simulation.

### cornish_fisher_k.json
Contains 100,00 samples of x at iteration 10 collected by first sampling for Uniform(0,1) and then plugging
it into the cornish-fisher expansion of x of order k (at n=10).
