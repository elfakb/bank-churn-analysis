# Credit Card Churn Analysis

🇹🇷 [Türkçe](README.tr.md)

Which credit-card customers are leaving, why, and is a retention campaign worth the cost?

**Result:** Churn is driven by behavior, not demographics. One segment ("Disengaging", 23% of customers) holds 63% of all churners. Contacting only customers with positive expected value (24% of the base) reaches 59% of churners, with an estimated net benefit of **~$30.6K/year** on this 10,127-customer portfolio (range: $7.1K to $49.1K).

📄 [Executive summary (PDF)](reports/executive_summary.pdf) · 📓 [Notebook](notebooks/churn_analysis.ipynb)

![Churn by segment](reports/figures/08_segments.png)

## Key findings

- **Churn rate is 16.1%** (1,627 of 10,127 customers).
- **Behavior matters, demographics don't.** Attrited customers made 45 transactions/year vs. 69 for others (Cohen's d = -1.24). Gender, education, income and card tier have negligible effects (Cramér's V ≤ 0.04).
- **Warning signs:** fewer products, more inactive months and more service contacts each raise churn (chi-square, p < 0.001).
- **"Disengaging" segment churns at 45%**, 2.8x the average.
- **Blanket campaigns lose money** in low-risk segments. Only individually targeted outreach pays.

## Recommended actions

| Segment | Action | Churn |
|---|---|---|
| Disengaging | Spend-triggered cashback + early-warning alert | 45% |
| Single-product, no revolving balance | Cross-sell a second product | 34% |
| Frequent service contacts | Service recovery (selective) | 11% |
| High-value stable | Relationship-manager review (selective) | 5% |

Each customer is scored and contacted only if expected value is positive:
`EV = p × save_rate × (revenue − incentive) − (1 − p) × redeem_rate × incentive − contact_cost`

## Assumptions and limits

- The dataset has no revenue column, so revenue is a proxy (1.8% interchange + 15% margin on revolving balance + annual fee). Campaign inputs: $2 contact cost, $25 cashback, 25% save rate. All are editable in the notebook.
- The save rate is the key unknown and should be validated with an A/B test.
- Behavioral features cover the same 12 months in which customers left, so they are early-warning signals, not proven causes.

## Methods

pandas cleaning (removed leaked columns, handled hidden `Unknown` values with a sensitivity check) · chi-square and t-tests with effect sizes and Holm correction · logistic regression and decision tree (5-fold CV, AUC 0.92 / 0.94) · USD scenario analysis.

## Run it

```bash
pip install -r requirements.txt
# download BankChurners.csv into data/ (see data/README.md)
jupyter nbconvert --to notebook --execute --inplace notebooks/churn_analysis.ipynb
python make_summary.py
```

**Stack:** Python, pandas, SciPy, statsmodels, scikit-learn, seaborn, Jupyter