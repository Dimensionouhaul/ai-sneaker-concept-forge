# ai-sneaker-concept-forge

A desktop tool that generates sneaker and footwear product concepts from a
prompt, a palette, and a silhouette seed. Built as a plugin host: the core
ships a window, a registry, a loader, and a render queue; every actual
generator is a plugin loaded at boot.

## What it produces

- **Silhouette sheets** — 2D orthographic sketches (medial, lateral, top).
- **Palette studies** — colorways applied to a base silhouette.
- **Material callouts** — upper / midsole / outsole breakdowns with texture
  swatches and stitch suggestions.
- **Concept boards** — a single PNG that packages the above with a name,
  a one-line story, and a SKU-style code.

## Pipeline

```
prompt + palette + silhouette seed
        │
        ▼
 ┌───────────────┐   ┌──────────────────┐   ┌─────────────────┐
 │ silhouette_gan│ → │ palette_diffusion│ → │ material_sampler│
 └───────────────┘   └──────────────────┘   └─────────────────┘
        │                     │                      │
        └──────────────┬──────┴──────────┬───────────┘
                       ▼                 ▼
                 brand_voice      concept_composer
                       │                 │
                       └────────┬────────┘
                                ▼
                        concept board (PNG)
```

## Plugin kinds

| Kind        | Contract                    | Example plugin       |
| ----------- | --------------------------- | -------------------- |
| `silhouette`| `SilhouettePlugin`          | `silhouette_gan`     |
| `palette`   | `PalettePlugin`             | `palette_diffusion`  |
| `material`  | `MaterialPlugin`            | `material_sampler`   |
| `voice`     | `VoicePlugin`               | `brand_voice`        |
| `composer`  | `ComposerPlugin`            | (built into host)    |

See `docs/PLUGINS.md` for the full contract reference.