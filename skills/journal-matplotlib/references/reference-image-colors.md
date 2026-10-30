# Reference image → proposal → confirmed colors

Use this route when the user supplies an image as a color reference or rejects the current choices. The required new-color confirmation comes from the user's requested workflow. Keep the rest of the figure work moving while waiting for that decision.

## Inspect and interpret

- Use the image already attached or linked; if none is available, invite an attachment in the normal conversation. Do not use a text-only input tool to ask for an upload. Do not require an upload when a clear text preference is sufficient to make a new proposal.
- Actually inspect the image with the available image/PDF viewer. Identify the intended panel or region; ask which region only when the ambiguity materially changes the proposal. Keep the reference in the task workspace, not the installed skill or a global preference store.
- Separate data-series colors, continuous colorbar, uncertainty/fill, annotations, background and neutral/reference marks. Large white backgrounds, dark axes, photographs and atom colors must not dominate a plot-series palette just because they occupy many pixels. If the reference is a photograph, use it as a visual mood source and state that the quantitative encoding is newly designed.
- Record source filename or URL, panel/region and acquisition method. Use `pixel_sampled_approximate` for raster sampling, `visually_estimated` when estimating by eye, and `vector_source` only when numerical values were actually read from a vector/source file. Screenshot/JPEG samples are approximate. Do not claim exact HEX or original scientific colorbar normalization from visual appearance alone.
- Identify the target plot type, group count and scientific meanings from existing context. If the reference lacks enough distinguishable colors, propose facets or explicitly derived additional colors. Do not cycle colors or silently invent an ordered scale from categorical samples.

## Build reviewable cards

Make one faithful candidate; add one readability-adjusted candidate when useful. If the source is unsuitable for the target marks, explain the issue and show the adjusted version instead of promising an exact match. Do not invent a third option merely to fill a template.

Each card needs an ID and revision, source/region, sampled source swatches, proposed swatches, explicit category mapping or colormap with numeric normalization, background/text/reference roles and band alpha. List any changes: darkened cyan for a white background, reduced fill alpha, replaced a low-contrast yellow line, or separated two similar groups. Clearly label derived colors.

Show a compact synthetic example with the same data and geometry across comparable cards, using the intended line, marker, band or field marks. For heatmaps show a labeled colorbar and meaningful midpoint. If scales are not yet known, mark normalization as pending and do not finalize a quantitative card until scientifically appropriate limits are established. Continuous ramps reconstructed from a handful of sampled anchors are newly interpolated maps, not recovered originals.

## Confirm and apply

Ask for the card ID/revision or a requested adjustment. A reply such as “use B” after two named cards is sufficient. “Looks good” is sufficient when it unambiguously refers to one presented card; clarify if multiple unresolved choices remain. Do not turn rejection, reference upload, elapsed time or an agent-generated message into approval. A later explicit instruction to choose and apply automatically is a valid delegation; preserve that actual instruction.

Record the human reply, selected card fingerprint and intended figure/project scope. Use `palette_cards.py confirm` only after that evidence exists, then `export` to obtain the approved settings. The helper checks record integrity; it cannot authenticate who wrote a quoted reply, so the agent remains responsible for verifying it came from the human user.

Apply the settings centrally to lines, markers, error bars/bands, legends, panel links and colorbars. Reuse the same semantic mapping for overview and standalone panels. Re-export and inspect PDF/PNG at final size. Preserve source data and scientific processing. Store the approval record beside the figure contract and reference it from `<stem>.figure.json`.

If the user dislikes the result, keep the old record as history, create a new card revision and repeat the choice. Do not apply newly tuned colors while waiting. Already confirmed colors may be reused in their approved scope; a new category mapping or normalization is a new choice. Layout-only fixes do not require another color confirmation.
