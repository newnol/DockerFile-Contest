[LỊCH SỬ - bài nộp 11/2025, đo trên macOS arm64, chưa kiểm chứng lại. Số hiện hành: measurement-data/github-42057474702/comparison/comparison.md]

# 📊 MEASUREMENT DATA - Evidence Package

> **Purpose:** Chứng minh các chỉ số đo được cho Ban Tổ Chức  
> **Date:** November 10, 2025  
> **Image:** app:contest (105 MB)  

---

## 📁 FILES IN THIS DIRECTORY

### 1. Image Size Evidence

**File:** `image-size.txt`

```bash
# Command used:
docker images app:contest

# Output shows:
REPOSITORY   TAG       IMAGE ID       CREATED       SIZE
app          contest   0935dd8d9ddf   2 hours ago   105MB
```

**Purpose:** Chứng minh image size = 105 MB

---

### 2. Layer Analysis

**File:** `docker-history.txt`

```bash
# Command used:
docker history app:contest --no-trunc

# Contains:
- Full layer information
- Each layer's size
- Complete command history
- Image optimization proof
```

**Purpose:** Chứng minh layer optimization và build strategy

**File:** `image-history.txt` (formatted version)

Phiên bản dễ đọc hơn với format table

---

### 3. Security Scan Reports

**Directory:** `security-scan/`

```
security-scan/
├── trivy-report.txt          # Human-readable scan results
├── trivy-full.json           # Full JSON report for automation
├── trivy-high-critical.json  # HIGH/CRITICAL CVEs only
└── SUMMARY.md                # Executive summary
```

**Key Evidence:**
- ✅ 0 CRITICAL vulnerabilities
- ✅ 0 HIGH vulnerabilities  
- ✅ 0 MEDIUM vulnerabilities
- ✅ 0 LOW vulnerabilities
- ✅ Security Score: 100/100

**Commands used:**
```bash
trivy image --severity HIGH,CRITICAL app:contest
trivy image --format json -o trivy-full.json app:contest
```

---

### 4. SBOM (Software Bill of Materials)

**Files:** Available in parent directory `contest-reports/`

```
contest-reports/
├── sbom.json              # Syft JSON format
├── sbom-cyclonedx.json   # CycloneDX format
└── sbom-spdx.json        # SPDX format
```

**Command used:**
```bash
syft app:contest -o json > sbom.json
syft app:contest -o cyclonedx-json > sbom-cyclonedx.json
syft app:contest -o spdx-json > sbom-spdx.json
```

**Purpose:** 
- Industry-standard SBOM formats
- Supply chain security
- Compliance requirements
- Bonus points: +5

---

## 🎯 HOW TO VERIFY

### Verify Image Size

```bash
docker images app:contest
# Expected: 105 MB
```

### Verify Layers

```bash
docker history app:contest
# Expected: 17 layers, largest = 43.2 MB (Python base)
```

### Verify Security

```bash
trivy image --severity HIGH,CRITICAL app:contest
# Expected: 0 vulnerabilities
```

### Verify SBOM

```bash
# If syft installed:
syft app:contest -o table
# Expected: 33 packages, all clean
```

---

## 📈 KEY METRICS SUMMARY

| Metric | Value | Evidence File |
|--------|-------|---------------|
| **Image Size** | 105 MB | `image-size.txt` |
| **Layer Count** | 17 | `docker-history.txt` |
| **CVE Count** | 0 | `trivy-report.txt` |
| **Security Score** | 100/100 | `SUMMARY.md` |
| **Package Count** | 33 | SBOM files |
| **Build Time** | 85s (cold) / 1.5s (warm) | See BENCHMARK_DATA.md |

---

## 🏆 BONUS POINTS EVIDENCE

### ✅ SBOM + Clean Scan (+10 points)

**Evidence:**
- ✅ `sbom*.json` files present
- ✅ `trivy-report.txt` shows 0 HIGH/CRITICAL
- ✅ Multiple scan formats provided

**Requirement:** SBOM + không có lỗi High/Critical  
**Status:** **PASSED** ✅

---

### ✅ Multi-arch Support (+3 points)

**Evidence:**
- ✅ `BUILD_MULTI_ARCH.md` documentation
- ✅ Tested on both arm64 and amd64
- ✅ Build commands provided

**Requirement:** Multi-arch manifest (buildx)  
**Status:** **DOCUMENTED & TESTED** ✅

---

## 📋 VERIFICATION COMMANDS FOR BTC

Copy-paste để verify nhanh:

```bash
# 1. Check image exists and size
docker images app:contest

# 2. Check layers
docker history app:contest | wc -l

# 3. Security scan (if Trivy installed)
trivy image --severity HIGH,CRITICAL app:contest

# 4. SBOM generation (if Syft installed)
syft app:contest -o table | head -20

# 5. Test run
docker run -d -p 8080:5000 --name app-test app:contest
sleep 15
curl http://localhost:8080/health/
docker stop app-test && docker rm app-test

# Expected results:
# - Size: 105 MB ✅
# - Layers: 17 ✅
# - CVEs: 0 ✅
# - Health: {"heartbeat":"HEALTHY"} ✅
```

---

## 📞 CONTACT

**Thí sinh:** newnol  
**Email:** contact@newnol.io.vn  
**Website:** https://newnol.io.vn

**Questions?** Email me anytime!

---

## 🔗 RELATED DOCUMENTATION

- 📦 **SUBMISSION_PACKAGE.md** - Overview & scoring
- 📊 **BENCHMARK_DATA.md** - Detailed measurements
- 🚀 **QUICK_START.txt** - Quick guide for BTC (5-10 lines)
- 🏗️ **BUILD_MULTI_ARCH.md** - Multi-architecture guide
- 📖 **HUONG_DAN_CHAY.md** - Complete documentation

---

**Last Updated:** November 10, 2025  
**Verification Status:** ✅ ALL PASSED  
**Ready for Submission:** ✅ YES

