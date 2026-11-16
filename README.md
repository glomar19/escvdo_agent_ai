# ESCVDO Competitor Trend Agent

An agent that turns competitor fashion photos into plain-language insights for a non-technical buyer: which garments, colours and patterns a competitor uses more or less than ESCVDO (Peruvian knitwear brand), and what to do about it.

![App screenshot](docs/app.png)

## Why

Buyers compare collections by eye. This project makes that comparison measurable: the same attributes, extracted the same way, for every brand.

## What it does

```
photos  ->  garment  ->  colour  ->  pattern  ->  gaps vs ESCVDO  ->  5 insights  ->  Streamlit app
```

| Step | How | Code |
|---|---|---|
| Collect photos | Saved collection pages (HTML) parsed with BeautifulSoup; one folder per brand and collection | `src/parse_saved_page.py`, `src/download_images.py` |
| Garment type | CLIP zero-shot, then logistic regression on CLIP embeddings | `src/classify.py` |
| Dominant colour | Background removal + k-means, upper and lower body separately | `src/colors.py` |
| Pattern | CLIP zero-shot, low-confidence predictions reported as "solid / other" | `src/classify.py` |
| Insights | Code computes the biggest gaps between brands, templates write the text | `src/report.py` |
| Interface | Streamlit: pick a competitor, read insights and charts | `app.py` |

Notebooks in `notebooks/`: `01_data_collection`, `02_classification`, `03_insights`.

## Data

- **ESCVDO:** 52 catalogue photos from 5 collections (FW25, PF25, PF26, PS26, SS26).
- **Chloé:** 53 runway looks from SS27 (60 downloaded, 7 non-look items removed).
- Every photo was **hand-labelled, multi-label** (one outfit can contain several garments): tops, bottoms, dresses, knitwear, outerwear.

Photos are not included in this repository (third-party material). The code, my labels and the result tables are.

## Results

**Garment classification** (F1 per garment, 5-fold cross-validation on the labelled photos):

| Garment | Photos | CLIP zero-shot | Trained on CLIP embeddings |
|---|---|---|---|
| Tops | 27 | 0.36 | 0.46 |
| Bottoms | 20 | 0.13 | 0.25 |
| Dresses | 35 | 0.62 | 0.62 |
| Knitwear | 48 | 0.27 | 0.95* |
| Outerwear | 23 | 0.72 | 0.86* |

\*Inflated: all 48 knitwear photos come from ESCVDO and 20 of the 23 outerwear photos from Chloé, so the model can partly learn the brand instead of the garment. Needs more brands for a fair test.

**Colour:** about 5 of 8 manually checked photos matched. **Pattern:** 6 of 8.

Because garment accuracy is still weak, the comparison between ESCVDO and Chloé uses the hand labels. The trained model is meant for new brands.

**Example insights (ESCVDO vs Chloé):**

- ESCVDO uses more knitwear: 92% of photos vs 0%.
- ESCVDO uses more stripes: 35% vs 0%.
- Chloé uses more outerwear: 38% vs 6%.

## What worked and what didn't

- **Single-label evaluation was misleading.** Labels taken from product names ("Lucero Top") don't describe outfits with several garments. Hand-labelling multi-label fixed the evaluation (42% strict accuracy became 56% hit rate under a fair criterion).
- **Zero-shot CLIP over-predicts "dress"** on full-body photos (71% predicted vs 37% real).
- **Colour:** the first version picked the studio or runway background (78% "beige" for Chloé). Removing the background row by row fixed most of it. Dark skin tones and very pale pastels still fail.
- **A 1.5B local LLM (Qwen2.5-1.5B-Instruct) hallucinated numbers** and drifted off-topic when asked to write the insights. I switched to a split: code computes, templates write. An LLM can be added back later as an optional polish step.
- **Scraping was unreliable:** two sites returned HTTP 429, so I saved the pages from the browser and parsed them locally.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt            # the app only (pandas, streamlit)
streamlit run app.py
```

The app reads `data/final_table.csv`. To re-run the full pipeline (CLIP, colours, notebooks) install `requirements-pipeline.txt` as well.

## Limitations

- Small dataset (about 105 photos, two brands).
- ESCVDO photos are catalogue shots and Chloé photos are runway looks, so the comparison is approximate.
- Colour and pattern are automatic and imperfect. ESCVDO's "animal print" and "polka dots" (about 14% of its photos) are probably open crochet texture mistaken for a print, some with high confidence (0.7 to 0.9), so the confidence threshold alone does not remove them.
- Garment classifier is confounded with brand (see above).

## Next steps

- Add more competitors (Ayni, Ulla Johnson) to break the brand confound.
- Let the user upload new photos and classify them live.
- Tests (`pytest`), Dockerfile and a FastAPI endpoint.

## Author

Gloria Morales. MSc Business Engineering (Data Analytics), Ghent University.
