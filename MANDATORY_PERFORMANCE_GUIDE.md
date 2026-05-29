# 1920x1080@60fps without GPU passthrough

> **Tested on:** QEMU 9.2.1, macOS Guest (Big Sur – Sequoia), Host OS: Ubuntu 24.04 / GNOME (X11)  
> **Display:** `vmware-svga` (no GPU passthrough)  
> **Note:** In macOS System Information (About This Mac) you will still see **3–7 MB of Video Memory** regardless of QEMU settings. This is expected and not a problem. The `vgamem_mb` parameter does not affect the macOS driver or framebuffer performance — do not chase this dead end.> **Resolution:** 1920×1080

---

## Core Principle

The entire point of this guide is to **find your highest-performing physical cores** and pin the macOS guest exclusively to them. You must **prevent the host scheduler from spreading QEMU threads — especially the software rendering pipeline — across slow or distant cores**, which introduces massive latency spikes and frame-pacing issues.

Modern CPUs are not symmetric. They contain:
- **P-cores** (fast) and **E-cores** (slow) on Intel
- **Multiple CCDs/CCXs** on AMD chiplet designs (e.g., Ryzen 3000/5000 series)
- **SMT/Hyper-Threading siblings** that share execution units

If QEMU is allowed to roam freely, a vCPU or the display thread will inevitably land on:
- an Intel E-core,
- an AMD CCX/CCD with high inter-core latency,
- or an SMT sibling fighting with a host process.

**The result is choppy 5–15 FPS slideshows instead of a smooth desktop.**

The solution is strict isolation: hand-pick the fastest physical cores, disable SMT, and lock QEMU to them with `taskset`.

---

## Quick Start: The `macos()` Function

Add this to your `~/.bashrc` or `~/.zshrc` (adjust the core numbers to your CPU):

```bash
macos() {
    # Example: 4 physical P-cores without SMT
    # Replace 0,1,3,6 with the correct cores for YOUR processor
    taskset -c 0,1,3,6 ./OpenCore-Boot.sh
}
```

Then simply run:
```bash
macos
```

You **must** also edit `./OpenCore-Boot.sh` to match the core count:

```bash
CPU_THREADS="4"
CPU_CORES="4"
CPU_SOCKETS="1"
```

---

## CPU Selection Methodology

### Step 1: Map your physical layout

Run:
```bash
lscpu -e
```

Identify:
- Which logical CPUs belong to the same **physical core** (SMT pairs)
- Which cores share the same **L3 cache** (CCX on AMD, or P-cores on Intel)
- Which cores are **E-cores** or **LP E-cores** (avoid entirely)

### Step 2: Pick the best cores

**Rules:**
1. **Never use E-cores** for QEMU. They lack the IPC and single-thread latency required for smooth UI.
2. **Prefer cores within the same CCX/L3 domain** to minimize cache coherency latency.
3. **Use 4–6 cores maximum.** More cores without strict pinning cause the scheduler to scatter threads across distant silicon, increasing cross-CCX/CCD latency and breaking frame-pacing.
4. **Always pick one thread per physical core** (disable SMT first — see below).

### Step 3: Use AI for precise core selection

Because every CPU has a unique core numbering map (SMT pairs are not always sequential), **feed your `lscpu -e` output to an AI assistant** and ask:

> *"I am running QEMU with a macOS guest. I want to pin the guest to my fastest 4 physical cores without SMT. Which logical CPU numbers should I use for `taskset`?"*

The AI will parse your exact CCX/CCD topology and give you the correct comma-separated list.

---

## Disable SMT / Hyper-Threading

SMT (Simultaneous Multithreading, called Hyper-Threading on Intel) allows one physical core to present two logical CPUs.

**Why it kills QEMU performance:**

When SMT is enabled and you pin QEMU to logical CPUs `0,1,2,3`, the **physical cores are still shared** with their SMT siblings (`12,13,14,15` on a 24-thread CPU). The host scheduler places gnome-shell, kernel workers, or QEMU helper threads on those siblings, causing contention for:
- Execution units (ALU, FPU)
- L1/L2 caches
- TLB

This produces **micro-stutters** that feel like low FPS even when the guest is technically rendering frames.

**Temporarily disable SMT (no reboot required):**
```bash
echo off | sudo tee /sys/devices/system/cpu/smt/control
```

**Re-enable later:**
```bash
echo on | sudo tee /sys/devices/system/cpu/smt/control
```

> **Recommendation:** For latency-sensitive guests (macOS desktop, gaming VMs), run with SMT **OFF**. The throughput loss is irrelevant; the latency gain is dramatic.

---

## Architecture Comparison: Why Some CPUs "Just Work" and Others Don't

| | **AMD Ryzen 7 5700G** | **AMD Ryzen 9 3900X** |
|---|---|---|
| **Architecture** | Zen 3 (Cezanne) — **Monolithic APU** | Zen 2 (Matisse) — **Chiplet (2×CCD)** |
| **Core Topology** | 8 identical cores, single L3, single memory controller | 12 cores split across 2 CCDs × 2 CCXs |
| **Cross-core Latency** | ~40 ns (uniform) | ~100 ns (intra-CCX), ~300–400 ns (cross-CCD) |
| **Integrated GPU** | **Vega 8** — handles host OpenGL compositing | **None** — relies on discrete GPU for host |
| **Why it was smooth** | All cores equal, iGPU accelerates QEMU window blit, no scheduler surprises | Without pinning, threads scattered across CCDs; with SMT on, host processes collided with vCPUs |
| **The Fix** | Not needed — works out of the box | **Disable SMT** + pin to a single CCD (cores 0–5) |

### What we achieved

On the **Ryzen 9 3900X**, before optimization:
- macOS guest was a laggy slideshow at 1920×1080
- UI felt like 5–10 FPS despite high host CPU usage

After **disabling SMT** and pinning to **4 physical cores on CCD 0** (`taskset -c 0,1,2,3`):
- **Smooth 1920×1080 desktop experience**
- No visible stuttering during window drag, Safari scrolling, or Launchpad animation
- Comparable "feel" to the Ryzen 7 5700G setup

The 3900X did not need more cores — it needed **clean, uncontended cores**.

---

## Important Warnings

### Do not over-allocate vCPUs

Using `CPU_THREADS=16` or `smp 16` in QEMU does **not** make macOS faster. Without pinning, it causes the host scheduler to spread software rendering and vCPU threads across:
- Slow E-cores (Intel)
- Distant CCXs/CCDs (AMD)
- SMT siblings already occupied by host processes

This creates **latency spikes** and **frame-pacing jitter** that feel far worse than running on 4 dedicated fast cores.

**Use 4–6 physical cores maximum**, strictly pinned.

### GPU matters for the host too

Even with perfect CPU pinning, the host needs a working OpenGL stack to composite the QEMU window efficiently.

- **5700G:** Vega 8 iGPU + `amdgpu` driver = excellent compositing performance.
- **3900X:** Requires a discrete GPU with working OpenGL drivers (tested successfully with NVIDIA RTX 5080). If the host falls back to `llvmpipe` (software OpenGL), the window will remain sluggish regardless of CPU pinning.

Verify your host renderer:
```bash
glxinfo | grep "OpenGL renderer"
```

If it says `llvmpipe`, fix your GPU drivers first.

---

## Tested Platforms

| Hardware | GPU | Required Optimization | Notes |
|---|---|---|---|
| **AMD Ryzen 7 5700G** | Radeon Vega 8 (iGPU) | **None** — works out of the box | Monolithic Zen 3 APU; no taskset needed for smooth 1920×1080 desktop |
| **Intel Core Ultra 7 155H** (Redmi Note) | Intel Arc Graphics | **`taskset` mandatory** | Hybrid P/E-core architecture; must pin to P-cores only |
| **AMD Ryzen 9 3900X** | NVIDIA RTX 5080 (host) | **`taskset` + SMT off mandatory** | Chiplet design; disabling SMT eliminated micro-stutters completely |

> All tests conducted at **1920×1080** using `vmware-svga` without GPU passthrough.

---

## TL;DR Checklist

1. [ ] Run `lscpu -e` and identify your fastest cores (use AI if unsure).
2. [ ] Disable SMT: `echo off | sudo tee /sys/devices/system/cpu/smt/control`.
3. [ ] Edit `OpenCore-Boot.sh`: `CPU_THREADS=4`, `CPU_CORES=4`.
4. [ ] Launch with `taskset -c <your-cores> ./OpenCore-Boot.sh`.
5. [ ] Verify host OpenGL is not `llvmpipe`.
6. [ ] Enjoy 1920×1080 macOS without GPU passthrough.
