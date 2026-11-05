# Presentation image sources and usage

These public project assets are used only to identify the projects discussed, not to imply endorsement, certification, successful deployment or measured security results. Original files are retained unchanged. The deck embeds them as base64 data URIs; no asset is fetched when viewing. SVGs were parsed and checked for scripts, event handlers, foreignObject and external image/href references before embedding.

## Official assets

| Local file | Official source | Provenance / usage notes |
|---|---|---|
| `docker.svg` | https://raw.githubusercontent.com/docker/docs/main/assets/icons/Whale.svg | Docker's own documentation repository, Whale icon. Repository API reports Apache-2.0; this is not a claim of unrestricted trademark permission. Docker brand guidance: https://www.docker.com/company/newsroom/media-resources/ |
| `github.png` | https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png | GitHub-hosted official mark, unmodified, including its white background. Identifies GitHub and the GHCR endpoint; not a separate invented GHCR logo. Use subject to GitHub logo/trademark guidance: https://github.com/logos . No independent image copyright license is asserted here. |
| `renovate.png` | https://raw.githubusercontent.com/renovatebot/renovate/main/docs/usage/assets/images/logo.png | Official Renovate documentation logo. Repository API reports AGPL-3.0; no asset-specific grant or trademark waiver was verified. Used for project identification, not as a new combined mark. |
| `wolfi.svg` | https://raw.githubusercontent.com/wolfi-dev/.github/main/profile/wolfi-logo-light-mode.svg | Official Wolfi organization profile, light-mode logo. Repository API returns no license. No reuse license is assumed; confirm permission before broader redistribution. Logo does not imply an approved or verified runtime base. |
| `grype.png` | https://user-images.githubusercontent.com/5199289/136855393-d0a9eef9-ccf1-4e2b-9d7c-7aad16a567e5.png | Linked as “Grype logo” by https://github.com/anchore/grype/blob/main/README.md . Complete mascot and wordmark retained. Grype repository API reports Apache-2.0; no independent image-specific grant or trademark waiver was verified. |
| `strix.png` | https://raw.githubusercontent.com/usestrix/strix/main/.github/logo.png | Official Strix repository image, original black square and clear space retained. Repository API reports Apache-2.0; no independent image-specific grant or trademark waiver was verified. Shown only inside the human-controlled optional lab. |
| `9router.svg` | https://raw.githubusercontent.com/decolua/9router/v0.4.41/public/favicon.svg | Official favicon from the exact proposal baseline tag, not a fabricated wordmark. Native orange gradient preserved as part of the official mark, not a new deck effect. Repository API reports MIT; no independent trademark waiver was verified. |

Repository-wide license metadata is context, not legal clearance for every brand asset. Ownership remains with the respective holders. Review the applicable upstream LICENSE and brand terms before public/commercial redistribution, especially assets without a verified image-specific license. Branch-based asset URLs are mutable; the SHA-256 inventory below identifies the precise downloaded copies.

## Authored editorial vectors

Four inline SVG illustrations were drawn specifically for this deck: slide 1 filesystem cutaway, slide 3 exploded layer side elevation, slide 7 build workspace and selected runtime artifact, and slide 9 process identity/file-permission boundary (replacing the generic shield). They are explanatory drawings, not official project graphics, screenshots, scanner output, benchmark data or generated raster art. No image-generation service was used.

## Placement

12 official asset placements across the deck: Docker on 1 and 14; 9router on 2 and 13; Wolfi on 8; Renovate on 10 and 14; Grype on 11 and 14; Strix on 13; GitHub on the Git and GHCR nodes on 14. Total enhanced slides: 10 (1, 2, 3, 7, 8, 9, 10, 11, 13, 14). Existing method diagrams, title sequence and speaker notes are preserved.

## Original-file SHA-256

```text
8a395df2fd644ae59bc49e2f58b4eaa6bc1a5f4484eb00f532d033123ae2e920  docker.svg
6d6ef7bede0416b6ebee2014be5852576dbce89235fe16ea5c44ed01bd522132  github.png
8680cbb7a7779b9014cbe42c2261b089c20a5f2415a5b6257fc5ef9aba049d71  renovate.png
c23a2422844c8fba34c547b464f3af310c7c9669d4897773804e97092533c4ed  wolfi.svg
c73939c5003a9bd10bbe79b7efaa6dde2f04c2ae05260d1c63b344bf646fb70d  grype.png
a6d5ca4b84523e651c7151d0bcb6bc0c132ecc311566bb48ed2da6c82efcb9eb  strix.png
ddf1676baefc0d0c9631ca3c89b9ea4ee604e5d2989f9cdf45cfd0d1260d3f01  9router.svg
```
