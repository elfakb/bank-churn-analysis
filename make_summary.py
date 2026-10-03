"""Builds reports/executive_summary.pdf from reports/results.json (run after the notebook)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

R = json.load(open("reports/results.json"))
seg, eco, sc, ev = R["segments"], R["segment_economics"], R["scenarios"], R["ev_plan"]
N = R["n_customers"]; s1 = seg["S1 Disengaging"]
RED, BLUE, GREY = colors.HexColor("#d1495b"), colors.HexColor("#1f4e79"), colors.HexColor("#555555")

h1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, textColor=BLUE, leading=20)
sub = ParagraphStyle("sub", fontName="Helvetica", fontSize=8.5, textColor=GREY, leading=11)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5, textColor=BLUE, spaceBefore=7, spaceAfter=2, leading=13)
body = ParagraphStyle("b", fontName="Helvetica", fontSize=8.8, leading=11.6)
small = ParagraphStyle("s", fontName="Helvetica", fontSize=7.3, textColor=GREY, leading=9.2)
kv = ParagraphStyle("kv", fontName="Helvetica-Bold", fontSize=15, textColor=RED, alignment=1, leading=17)
kl = ParagraphStyle("kl", fontName="Helvetica", fontSize=7.4, textColor=GREY, alignment=1, leading=9)
cell = ParagraphStyle("c", fontName="Helvetica", fontSize=7.8, leading=9.6)
cellb = ParagraphStyle("cb", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)

doc = SimpleDocTemplate("reports/executive_summary.pdf", pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=12*mm, bottomMargin=10*mm,
                        title="Credit Card Churn - Executive Summary", author="")
W = A4[0] - 30*mm
S = []
S.append(Paragraph("Credit Card Churn: Who Leaves, Why, and What to Do", h1))
S.append(Paragraph(f"Executive summary &nbsp;|&nbsp; Kaggle 'Credit Card Customers' dataset, {N:,} customers &nbsp;|&nbsp; All money in USD", sub))
S.append(Spacer(1, 6))

def kpi(v, l): return [Paragraph(v, kv), Paragraph(l, kl)]
k = Table([[kpi(f"{R['churn_rate']:.1%}", f"churn rate<br/>({R['n_churners']:,} of {N:,} customers)"),
            kpi(f"{s1['share_of_all_churners']:.0%}", f"of churners sit in the 'Disengaging'<br/>segment ({s1['customers']/N:.0%} of customers)"),
            kpi(f"${sc['Base']['net']/1000:,.1f}K", f"net benefit / year, base case<br/>(this {N:,}-customer portfolio)"),
            kpi(f"{ev['share_of_churners_reached']:.0%}", f"of churners reached by contacting<br/>only {ev['contacted']/N:.0%} of customers")]],
          colWidths=[W/4]*4)
k.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), .6, colors.HexColor("#cccccc")), ("INNERGRID", (0, 0), (-1, -1), .3, colors.HexColor("#dddddd")),
                       ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7f9fb")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
S.append(k)

S.append(Paragraph("What we found", h2))
tt = R["t_tests"]; chi = R["chi_square"]
maxdemo = max(chi[c]["cramers_v"] for c in ["Gender", "Education_Level", "Marital_Status", "Income_Category", "Card_Category", "Dependent_count"])
bul = [
 f"<b>Churn is a behavior problem.</b> Attrited customers made {tt['Total_Trans_Ct']['mean_attrited']:.0f} transactions a year vs. {tt['Total_Trans_Ct']['mean_existing']:.0f} for existing ones "
 f"(Cohen's d = {tt['Total_Trans_Ct']['cohens_d']:.2f}, a large effect), and their transaction count fell sharply from Q1 to Q4. Gender, education, marital status, income and card tier "
 f"are each weak predictors on their own (Cramer's V &lt;= {maxdemo:.2f}).",
 "<b>Warning signs are visible and measurable:</b> fewer products held, more months inactive and more service contacts each raise churn risk (chi-square, Holm-corrected p &lt; 0.001).",
 f"<b>Where to look:</b> the 'Disengaging' segment ({s1['customers']:,} customers) churns at {s1['churn_rate']:.0%}, {s1['lift_vs_avg']:.1f}x the average; "
 f"single-product customers with no revolving balance churn at {seg['S2 Single-product, no revolving']['churn_rate']:.0%}.",
]
for b in bul: S.append(Paragraph("&bull; " + b, body)); S.append(Spacer(1, 1.5))

S.append(Paragraph("Recommended actions by segment", h2))
rows = [[Paragraph(x, cellb) for x in ["Segment", "Customers", "Churn", "Action", "Break-even save rate*", "Net if contacted in full"]]]
act = {"S1 Disengaging": "Reactivation: spend-triggered cashback + early-warning alert",
       "S2 Single-product, no revolving": "Relationship bundle: cross-sell 2nd product, fee/rate benefit",
       "S3 Service friction": "Service recovery: senior callback, root-cause fix (selective)",
       "S4 High-value stable": "Priority care: relationship-manager review (selective)"}
for name in ["S1 Disengaging", "S2 Single-product, no revolving", "S3 Service friction", "S4 High-value stable"]:
    e, g = eco[name], seg[name]
    rows.append([Paragraph(name, cell), Paragraph(f"{g['customers']:,.0f}", cell), Paragraph(f"{g['churn_rate']:.0%}", cell), Paragraph(act[name], cell),
                 Paragraph(f"{e['breakeven_save_rate']:.0%}", cell), Paragraph(("-" if e['net'] < 0 else "") + f"${abs(e['net']):,.0f}", cell)])
t = Table(rows, colWidths=[33*mm, 21*mm, 13*mm, W - 33*mm - 21*mm - 13*mm - 26*mm - 27*mm, 26*mm, 27*mm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), BLUE), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#cccccc")),
                       ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f9fb")]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
S.append(t)
S.append(Paragraph("*Save rate at which the full-segment campaign breaks even (assumed rate: 25%). Blanket outreach loses money where churn is lower, so contact only customers with positive expected value.", small))

S.append(Paragraph("What it is worth", h2))
b, p, o = sc["Base"], sc["Pessimistic"], sc["Optimistic"]
S.append(Paragraph(
 f"Scoring every customer with the churn model and contacting only those whose expected value is positive means reaching <b>{ev['contacted']:,.0f} of {N:,} customers</b> "
 f"(cost ${ev['cost']:,.0f}, expected saves ~{ev['saved']:,.0f} customers). Base case: <b>${b['net']:,.0f} net per year</b> (ROI {ev['net']/ev['cost']:.0%}). "
 f"If only 10% of at-risk customers are retained: ${p['net']:,.0f}; at 35%: ${o['net']:,.0f}. "
 f"Scaled linearly to a 1M-customer book (illustration): about <b>${b['net_per_1m']/1e6:,.1f}M per year</b> (range ${p['net_per_1m']/1e6:,.1f}M to ${o['net_per_1m']/1e6:,.1f}M).", body))

fig = Image("reports/figures/09_sensitivity.png", width=78*mm, height=78*mm*4.2/8.5)
a = R["assumptions"]
txt = [Paragraph("Key assumptions (all editable in the notebook)", ParagraphStyle("x", parent=body, fontName="Helvetica-Bold", fontSize=8.5)),
       Paragraph(f"Revenue = {a['interchange_rate']:.1%} interchange on spend + {a['revolve_margin']:.0%} margin on revolving balance + annual fee. "
                 f"Contact cost ${a['contact_cost']:.0f}; cashback ${a['incentive']:.0f}, also claimed by {a['redeem_nonchurn']:.0%} of non-churners. "
                 f"Save rate {a['save_rate']:.0%} (to be validated). One-year benefit only, measured on churners' current (already reduced) activity: conservative.", small),
       Spacer(1, 4),
       Paragraph("Next steps", ParagraphStyle("y", parent=body, fontName="Helvetica-Bold", fontSize=8.5)),
       Paragraph("1) A/B test: hold out ~10% of the target list as control to measure the true save rate. "
                 "2) Rebuild the score on a lagged window so alerts fire before customers disengage. "
                 "3) Replace the revenue proxy with real P&amp;L data.", small)]
two = Table([[fig, txt]], colWidths=[82*mm, W - 82*mm])
two.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
S.append(Spacer(1, 4)); S.append(two)
doc.build(S)
