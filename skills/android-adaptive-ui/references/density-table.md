# Android Density Qualifiers & Resource Strategy

## Density Bucket Reference

| Qualifier | DPI Range | Scale | Typical Devices |
|---|---|---|---|
| `ldpi` | ~120 dpi | 0.75× | Legacy/low-end devices |
| `mdpi` | ~160 dpi | 1.0× (baseline) | HVGA phones, baseline reference |
| `hdpi` | ~240 dpi | 1.5× | Mid-range phones |
| `xhdpi` | ~320 dpi | 2.0× | Pixel 3a, typical mid-range 2024 |
| `xxhdpi` | ~480 dpi | 3.0× | Most flagship phones (Pixel 8, Galaxy S24) |
| `xxxhdpi` | ~640 dpi | 4.0× | Pixel 9 Pro, Galaxy S25 Ultra |
| `tvdpi` | ~213 dpi | 1.33× | Android TV (720p) |
| `nodpi` | any | 1.0× (no scaling) | Assets that must never be scaled (e.g., exact-size bitmaps) |
| `anydpi` | any | vector / intrinsic | Vector drawables, adaptive icons |

**Scaling ratio:** 3:4:6:8:12:16 (ldpi : mdpi : hdpi : xhdpi : xxhdpi : xxxhdpi)

---

## Pixel Size Cheat Sheet (48dp Baseline Icon)

| Qualifier | px size |
|---|---|
| ldpi | 36 × 36 px |
| mdpi | 48 × 48 px |
| hdpi | 72 × 72 px |
| xhdpi | 96 × 96 px |
| xxhdpi | 144 × 144 px |
| xxxhdpi | 192 × 192 px |

Formula: `px = dp × (dpi / 160)`

---

## Resource Folder Strategy

### Bitmaps (PNG / WebP)
- Minimum: provide `drawable-mdpi` and `drawable-xxhdpi`
- Recommended: add `drawable-xhdpi` for mid-range device quality
- Optional: `drawable-xxxhdpi` (launcher icons, splash screens only — most bitmaps don't benefit)
- Do **not** put bitmaps in `drawable/` alone — that folder is treated as mdpi and upscaled 3× on flagship phones, producing blurry assets

### Vectors
- Put one file in `drawable/` (or `drawable-anydpi/` for explicit clarity)
- Replaces all density buckets — no density folder needed
- `drawable-anydpi-v26` overrides bitmaps for adaptive icons on API 26+

### App Icons
- Always use `mipmap-*` folders, never `drawable-*`
- Provide all six density buckets for the foreground layer
- Use `mipmap-anydpi-v26` for adaptive icons (foreground + background layers)

### Summary Table

| Asset Type | Folder Strategy |
|---|---|
| App icon (bitmap) | `mipmap-mdpi` through `mipmap-xxxhdpi` |
| App icon (adaptive) | `mipmap-anydpi-v26` + density bitmaps as fallback |
| UI bitmap | `drawable-mdpi` + `drawable-xxhdpi` minimum |
| Vector drawable | `drawable/` (single file) |
| Exact-size asset | `drawable-nodpi/` |
| Background image | `drawable-xxhdpi/` + `drawable-xxxhdpi/` |

---

## Compose vs. XML Density Behavior

| Context | How density works |
|---|---|
| Compose `Modifier.size(48.dp)` | Dp is a Compose unit — the framework converts to px automatically using screen density. You never specify px. |
| `ImageVector` / `Icons.*` | Density-independent by definition — renders at correct size on any screen without resource folders. |
| `painterResource(R.drawable.my_image)` | Loads from the density-appropriate `drawable-*` folder at runtime. Provide density variants. |
| `BitmapFactory.decodeResource()` | Same as above — loads density-appropriate bitmap. |
| View-based XML layout `android:layout_width="48dp"` | Converted by the View system — same rules as Compose dp. |

**In Compose:** if you need a pixel value (e.g., for `Canvas` drawing), convert explicitly:
```kotlin
val pxValue = with(LocalDensity.current) { 48.dp.toPx() }
```

---

## Anti-Patterns

| Anti-pattern | Why it's wrong | Fix |
|---|---|---|
| `Modifier.size(144.px)` in Compose | `px` is absolute and ignores screen density — looks wrong on every non-reference device | Use `.dp`: `Modifier.size(48.dp)` |
| Putting bitmaps only in `drawable/` | Equivalent to mdpi; upscaled 3× on xxhdpi phones → blurry | Add `drawable-xxhdpi/` variant |
| `android:anyDensity="false"` in manifest | Disables the density scaling system entirely — all bitmaps render at raw pixel size | Remove this attribute |
| Using `resources.displayMetrics.density` for layout decisions | Use `WindowSizeClass` for layout decisions; density is only for px conversion | Use `currentWindowAdaptiveInfo().windowSizeClass` |
| Providing only `drawable-xxxhdpi` assets | Downscaled to lower densities — wastes memory on mid-range devices | Provide density-appropriate variants |
