# GSoC 2026 Proposal: Oxidizing EKO – Rust Integration for High-Performance DGLAP Evolution

## 1. Synopsis
EKO is a critical Python library under NNPDF that solves DGLAP evolution equations for Parton Distribution Functions (PDFs). This project aims to "oxidize" the library by rewriting its performance-critical numerical components in Rust. The primary goal is to preserve EKO's flexible Python API while leveraging Rust's safety and speed, ultimately delivering production-ready integrations across Python, C++, and Fortran interfaces, backed by automated packaging and benchmarking.

## 2. Motivation and Background
In high-energy particle physics, precise theoretical predictions for colliders like the LHC rely heavily on Parton Distribution Functions (PDFs). To fit these PDFs accurately, researchers must repeatedly solve the DGLAP (Dokshitzer-Gribov-Lipatov-Altarelli-Parisi) evolution equations. Because PDF fitting loops run these calculations millions of times, performance is a strict bottleneck.

"Oxidation" in this context refers to replacing heavy computational kernels natively written in Python (or wrapped in older C-extensions) with heavily optimized Rust code. Rust is the perfect tool for this: it matches the raw performance of C++, entirely eliminates memory safety bugs, and boasts a phenomenal ecosystem for interoperability. By oxidizing EKO's slow paths, we can maintain the expressive flexibility of Python for physicists while providing a blazingly fast backend that seamlessly targets existing C++ and Fortran pipelines.

## 3. My Mathematical Background
Solving integro-differential equations logically requires strong foundations in calculus, linear algebra, and complex analysis. 

I scored in the 98th percentile in IIT JEE Advanced, which requires being among the top 1-2% of roughly 180,000 candidates across Asia in mathematics, physics, and chemistry. The mathematics section covers calculus, complex numbers, linear algebra, and combinatorics at a level I found directly relevant to this domain's requirements. 

During my studies, I implemented numerical ODE solvers (Euler, Runge-Kutta 4th order) from scratch in Python and benchmarked their convergence rates. This is directly related to the integro-differential nature of DGLAP equations. Furthermore, I built a PageRank implementation using power iteration on sparse matrices, which gave me hands-on understanding of how large linear algebra problems (like eigendecomposition and matrix operations) are safely structured and solved efficiently.

The Beta function evaluation task was genuinely interesting to me. It required understanding the change of variables $\theta = (\pi/2)t$, why the Jacobian $\pi/2$ gets absorbed into the Rust kernel, and why `rep2` natively converges faster. As a demonstration of this mathematical maturity, here is a short proof that $B(1/2, 1/2) = \pi$, validating the results recovered by our benchmark:

We know the relationship between the Beta and Gamma functions:
$$B(\alpha, \beta) = \frac{\Gamma(\alpha)\Gamma(\beta)}{\Gamma(\alpha+\beta)}$$

So, $$B(1/2, 1/2) = \frac{\Gamma(1/2)^2}{\Gamma(1)}$$

By definition, we need $\Gamma(1/2)$:
$$\Gamma(1/2) = \int_0^\infty t^{-1/2} e^{-t} dt$$

Substitute $t = u^2$, which gives $dt = 2u \, du$:
$$= \int_0^\infty u^{-1} e^{-u^2} \cdot 2u \, du = 2\int_0^\infty e^{-u^2} du$$

This evaluates to the standard Gaussian integral, $\sqrt{\pi}$. Therefore:
$$B(1/2, 1/2) = \frac{(\sqrt{\pi})^2}{\Gamma(1)} = \frac{\pi}{1} = \pi$$

This perfectly validates our benchmark's output (`3.1415926536`), demonstrating an understanding of *why* the code converges to $\pi$, rather than just executing it.

## 4. Technical Approach
The focus of this project is building safe, performant kernels and managing language boundaries effectively.

**Rust/PyO3/Maturin Integration Patterns:** 
The inner loops of the integral equations will be ported to Rust. I will use PyO3 to create thin, zero-cost bindings to EKO's Python API, ensuring the Rust structs act efficiently as native Python objects. Maturin will be utilized as the build backend to orchestrated PEP 517 compliance, making installation completely transparent to developers via `pip`.

**C++ and Fortran Interoperability:** 
EKO must communicate with legacy physics infrastructure. I will expose the Rust kernels to C++ by meticulously designing `extern "C"` FFI boundaries that handle opaque pointers safely. For Fortran interoperability, I will leverage `ISO_C_BINDING` to map Rust's C-compatible structures directly to Fortran numerical arrays and subroutines safely. 

**Benchmarking Strategy:** 
The primary benchmarking strategy prioritizes mathematical accuracy first (e.g., matching the `scipy.special` output within a $1e^{-11}$ tolerance), before profiling for execution speed. Using exactly the framework created for the evaluation task, we will benchmark the Oxidized kernels rigorously across varying data loads and edge cases. We will compare our Rust performance explicitly against the existing `numba` JIT fallback layers to definitively prove our performance improvements.

**CI/CD Pipeline Automation:** 
Using GitHub Actions and `maturin publish`, I will automate the generation of manylinux, macOS, and Windows wheels on every Pull Request. This strictly ensures that any integrations on the CI fail if numerical precision diverges and that installing the package remains as simple as `pip install eko`.

## 5. Deliverables by Milestone
The project is scoped across three phases over roughly 14 weeks (175 hours):

**Phase 1: Familiarization, Setup, and CI Automation (Weeks 1-4, ~50hrs)**
- Set up the initial EKO-Rust repository scaffolding with PyO3 and Maturin.
- Identify the first mathematically dense performance bottlenecks in the DGLAP loops for translation.
- Configure exhaustive GitHub Actions to build and test Python wheels effectively across POSIX architectures and Windows.

**Phase 2: C++/Fortran Interfaces and Full Integration (Weeks 5-10, ~80hrs)**
- Design the `extern "C"` bindings for the oxidized kernels.
- Write C++ headers and Fortran modules mapping directly via `ISO_C_BINDING`.
- Integrate the Rust kernels natively within EKO's Python iterations.
- Implement integration tests validating exact computational accuracy against legacy implementations.

**Phase 3: Benchmarking, Documentation, and Polish (Weeks 11-14, ~45hrs)**
- Establish automated Pytest benchmarks measuring Rust versus Numba JIT versus pure Python loops natively.
- Draft necessary API documentation illustrating how to dynamically load or compile EKO natively.
- Provide a summary report detailing the peak performance jumps observed across the modules and proposing potential futures.

## 6. My Evaluation Task Results
During the evaluation task, I successfully built a hybrid Rust+Python library computing the Euler Beta function optimally:
- **Performance:** My Rust `rep1` implementation executed in just **0.0013s**, while the `rep2` transformation was even faster at **0.0007s** (handling the integrand boundary behavior significantly smoother).
- **Accuracy:** The generated results fully matched `scipy.special.beta` to a stringent accuracy of $1e^{-11}$ for numerical tests.
- **Verification:** Using the proof above, the integral rigorously recovered $B(0.5, 0.5) = \pi$.
- **Robustness:** Full support natively included complex $\alpha$ components, a Numba fallback interoperability layer, and profound memory efficiency (with overhead peaking tightly at a minuscule 3-5KB footprint).

## 7. Why I am a Good Fit
As the maintainer of the *Hyphae* project under LF Energy (Linux Foundation), I have strong experience collaborating in vast open-source environments, managing continuous CI/CD pipelines, and writing professional documentation for technical audiences. Additionally, my selection for the prominent Code for GovTech (C4GT) 2025 program involved building production-grade decentralized applications for the Indian government—teaching me the consequences of writing code correctly under scale constraints.

To be honest, I am actively improving my expertise across Rust lifetimes and advanced abstractions. However, I am a very fast learner, as demonstrated by the PyO3 execution in the evaluation task. Combining my mathematical foundations (JEE 98th percentile), my production open-source architectural experience gracefully bridging Python and System calls, and my growing proficiency in zero-cost Rust abstractions—I am highly motivated and ready to deliver production-quality code for NNPDF and EKO.

## 8. Timeline
- **Pre-GSoC (May):** Discuss the initial bottlenecks with mentors; explore the codebase structure; refine architectural targets natively.
- **Week 1-2 (Phase 1):** PyO3/Maturin scaffolding; begin translating first target loops to Rust.
- **Week 3-4 (Phase 1):** Write CI Actions workflows; configure GitHub CI test runners for the Python testing suite natively.
- **Week 5-7 (Phase 2):** Develop dense FFI boundaries `extern "C"`; rigorous memory leak checks and validation natively.
- **Week 8-10 (Phase 2):** Outline Fortran `ISO_C_BINDING` modules; compile cross-integrated application runs correctly. 
- **Week 11-12 (Phase 3):** Stress tests, comprehensive benchmarking versus purely Numba pipelines.
- **Week 13 (Buffer):** Buffer allocated for fixing unforseen scaling bugs or complex cross-language compilation link failures.
- **Week 14 (Final Phase):** Code cleanups, detailed markdown documentation, finalizing the project submission logs.

## 9. References
- **Altarelli, G., & Parisi, G.** (1977). Asymptotic freedom in parton language. *Nuclear Physics B*, 126(2), 298-318.
- **NNPDF Collaboration.** *EKO (Evolution Kernel Operators) Documentation and Source*.
- **PyO3 / Maturin Developer Guidelines.** Seamless Rust-Python Zero-cost Interfaces natively.
