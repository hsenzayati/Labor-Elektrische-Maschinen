"""Auswertung Versuch 2 - Drehstromtransformator (Messung vom 05.11.2026).

Erzeugt alle Abbildungen in ./abbildungen und schreibt die berechneten
Kennwerte nach ./abbildungen/kennwerte.txt.

Aufruf:  python3 auswertung.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HIER = Path(__file__).resolve().parent
DATEN = HIER / "Messdaten_05_11_26"
AUS = HIER / "abbildungen"
AUS.mkdir(exist_ok=True)

# Nenndaten des Prüflings (Versuchsanleitung, Tabelle 2)
U_N_STR = 220.0       # V, primäre Strangspannung
I_N_STR = 45.5        # A, Strangstrom
S_N = 3 * U_N_STR * I_N_STR

plt.rcParams.update({
    "font.size": 10, "axes.grid": True, "grid.alpha": 0.4,
    "figure.dpi": 150, "savefig.bbox": "tight",
})

log = []


def out(text=""):
    print(text)
    log.append(text)


def lese_csv(pfad, skip=1):
    zeilen = pfad.read_text(encoding="latin-1").splitlines()[skip:]
    werte = []
    for z in zeilen:
        teile = [t.strip().replace(",", ".") for t in z.split(";")]
        try:
            werte.append([float(t) for t in teile[:6]])
        except ValueError:
            continue
    return np.array(werte)


# ---------------------------------------------------------------- Leerlauf
ll = lese_csv(DATEN / "leerlaufkennlinie.csv")
U0, I0, P0, Q0, S0, cos0 = ll.T

I0N = np.interp(U_N_STR, U0, I0)
P0N = np.interp(U_N_STR, U0, P0)
Q0N = np.interp(U_N_STR, U0, Q0)
R_FE = U_N_STR**2 / (P0N / 3)
X_H = U_N_STR**2 / (Q0N / 3)

out("=== Leerlauf ===")
out(f"I0 bei U_N        = {I0N:.2f} A  ({100*I0N/I_N_STR:.2f} % von I_N)")
out(f"P0 bei U_N        = {P0N:.0f} W  ({100*P0N/S_N:.2f} % von S_N)")
out(f"Q0 bei U_N        = {Q0N:.0f} var")
out(f"cos phi0 bei U_N  = {P0N/np.hypot(P0N, Q0N):.3f}")
out(f"R_Fe (Strang)     = {R_FE:.0f} Ohm")
out(f"X_h  (Strang)     = {X_H:.1f} Ohm")
out(f"L_h  (Strang)     = {X_H/(2*np.pi*50):.3f} H")
out(f"Faktor I0(286V)/I0(220V) = {I0[-1]/I0N:.1f}")

fig, ax = plt.subplots(figsize=(6.5, 3.8))
ax.plot(I0, U0, "o-", ms=4)
ax.set_xlabel(r"Leerlaufstrom $I_0$ [A]")
ax.set_ylabel(r"Strangspannung $U_0$ [V]")
fig.savefig(AUS / "leerlaufkennlinie.pdf")
plt.close(fig)

b_fe = np.sum(P0 * U0**2) / np.sum(U0**4)
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4))
axs[0].plot(U0, P0, "o-", ms=4)
axs[0].set_ylabel(r"Wirkleistung $P_0$ [W]")
axs[1].plot(U0, Q0, "o-", ms=4, color="tab:red")
axs[1].set_ylabel(r"Blindleistung $Q_0$ [var]")
for a in axs:
    a.set_xlabel(r"Strangspannung $U_0$ [V]")
fig.tight_layout()
fig.savefig(AUS / "leerlaufleistung.pdf")
plt.close(fig)
out(f"Regression P0 = {b_fe*1e3:.3f} mW/V^2 * U^2")

# ------------------------------------------------------------ Kurzschluss
def kurzschluss(name, I_bez):
    zeilen = (DATEN / name).read_text(encoding="latin-1").splitlines()
    u_pri, u_sec = [float(x.replace(",", ".")) for x in zeilen[1].split(";")[:2]]
    d = lese_csv(DATEN / name, skip=3)
    Uk, Ik, Pk, Qk, Sk, cosk = d.T
    Zk = Uk / Ik
    Rk = Pk / 3 / Ik**2
    Xk = Qk / 3 / Ik**2
    # Ausgleichsgerade U_k = Z_k * I_k durch den Ursprung
    # Ausgleich über die Leistungen (alle drei Stränge): P = 3 R I^2, Q = 3 X I^2
    R = np.sum(Pk / 3 * Ik**2) / np.sum(Ik**4)
    X = np.sum(Qk / 3 * Ik**2) / np.sum(Ik**4)
    Z = np.hypot(R, X)
    Z_U = np.sum(Uk * Ik) / np.sum(Ik**2)   # aus der angezeigten Strangspannung
    UkN = Z * I_bez
    PkN = 3 * R * I_bez**2
    res = dict(u_pri=u_pri, u_sec=u_sec, ue=u_pri / u_sec, d=d, Z=Z, R=R,
               X=X, UkN=UkN, uk=UkN / U_N_STR, PkN=PkN, ur=R * I_bez / U_N_STR,
               ux=X * I_bez / U_N_STR, cosk=R / Z, Ibez=I_bez,
               Zk=Zk, Rk=Rk, Xk=Xk, Z_U=Z_U)
    out(f"=== Kurzschluss {name} ===")
    out(f"Übersetzung U1/U2 = {u_pri}/{u_sec} = {res['ue']:.3f}")
    for row, z, r, x in zip(d, Zk, Rk, Xk):
        out(f"  U={row[0]:6.2f} I={row[1]:6.2f} P={row[2]:7.0f}  Zk={z:.4f} Rk={r:.4f} Xk={x:.4f}")
    out(f"Z_k aus U/I (Ausgleich) = {Z_U:.4f} Ohm, aus S/(3I^2): " + ", ".join(f"{x:.4f}" for x in Sk/3/Ik**2))
    out(f"Z_k={Z:.4f} R_k={R:.4f} X_k={X:.4f} Ohm, cos phi_k={R/Z:.3f}")
    out(f"Bezugsstrom {I_bez:.2f} A: U_k={UkN:.2f} V, u_k={100*UkN/U_N_STR:.2f} %, "
        f"u_R={100*res['ur']:.2f} %, u_X={100*res['ux']:.2f} %, P_kN={PkN:.0f} W")
    return res


I1N_YZ = I_N_STR * np.sqrt(3) / 2   # primärer Bemessungsstrom bei Yz (39,4 A)
kyy = kurzschluss("KurzschlussYY.csv", I_N_STR)
kyz = kurzschluss("KurzschlussYZ.csv", I1N_YZ)
out(f"YZ bezogen auf 45,5 A: u_k={100*kyz['Z']*I_N_STR/U_N_STR:.2f} %")

fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4))
for k, mk, lab in [(kyy, "o-", "Yy"), (kyz, "s-", "Yz")]:
    o = np.argsort(k["d"][:, 1])
    Uk, Ik, Pk = k["d"][o, 0], k["d"][o, 1], k["d"][o, 2]
    axs[0].plot(Ik, Uk, mk, ms=4, label=lab)
    axs[1].plot(Ik, Pk, mk, ms=4, label=lab)
for a in axs:
    a.set_xlabel(r"Strangstrom $I_k$ [A]")
    a.legend(loc="upper left")
axs[0].set_ylabel(r"Strangspannung $U_k$ [V]")
axs[1].set_ylabel(r"Wirkleistung $P_k$ [W]")
fig.tight_layout()
fig.savefig(AUS / "kurzschluss.pdf")
plt.close(fig)

# ------------------------------------------------------------- Belastung
txt = (DATEN / "Belastungsmessung.csv").read_text(encoding="latin-1").splitlines()
def block(start):
    rows = []
    for z in txt[start:start + 3]:
        t = [x.strip() for x in z.split(";")]
        rows.append([float(x.replace(",", ".")) for x in t[:6]] + [t[6]])
    return rows
prim = block(3)
sek = block(9)
ue_leer = 2 / np.sqrt(3)   # Bemessungsübersetzung Yz (Aufgabe 2)
out("=== Belastung (Schaltung Yz) ===")
bel = []
for p, s in zip(prim, sek):
    U1, I1, P1, Q1, S1, c1, fall = p
    U2, I2, P2, Q2, S2, c2, _ = s
    eta = P2 / P1
    U20 = U1 / ue_leer
    dU = (U20 - U2) / U20
    U20m = U1 / kyz["ue"]          # mit gemessener Übersetzung 1,175
    dUm = (U20m - U2) / U20m
    bel.append(dict(fall=fall, U1=U1, I1=I1, P1=P1, Q1=Q1, c1=c1, U2=U2, I2=I2,
                    P2=P2, Q2=Q2, c2=c2, eta=eta, PV=P1 - P2, U20=U20, dU=dU,
                    ueU=U1 / U2, ueI=I2 / I1, dUm=dUm))
    out(f"{fall:24s} eta={100*eta:.1f} %  P_V={P1-P2:.0f} W  U1/U2={U1/U2:.3f} "
        f"I2/I1={I2/I1:.3f}  U20={U20:.1f} V  dU={100*dU:+.2f} %  (mit ü=1,175: {100*dUm:+.2f} %)")
    # Erwartete Verluste aus Ersatzschaltbild
    P0e = np.interp(U1, U0, P0)
    Pcu = 3 * kyz["R"] * I1**2
    out(f"   erwartet: P0={P0e:.0f} W + PCu={Pcu:.0f} W = {P0e+Pcu:.0f} W")
    bel[-1].update(P0e=P0e, Pcue=Pcu)
    # Kappsche Näherung des Spannungsfalls (bezogen auf Sekundärseite)
    sinphi = np.sqrt(1 - c2**2) * (-1 if "kapazitiv" in fall else 1)
    dU_kapp = I1 * (kyz["R"] * c2 + kyz["X"] * sinphi) / U1
    bel[-1]["dU_kapp"] = dU_kapp
    out(f"   Kapp: dU = {100*dU_kapp:+.2f} %")

x = np.arange(3)
namen = ["ohmsch", "ohmsch-induktiv", "ohmsch-kapazitiv"]
fig, axs = plt.subplots(1, 2, figsize=(7.6, 3.4))
axs[0].bar(x - 0.2, [b["P1"] / 1e3 for b in bel], 0.4, label="primär")
axs[0].bar(x + 0.2, [b["P2"] / 1e3 for b in bel], 0.4, label="sekundär")
axs[0].set_ylabel("Wirkleistung $P$ [kW]")
axs[1].bar(x - 0.2, [b["U1"] for b in bel], 0.4, label="primär")
axs[1].bar(x + 0.2, [b["U2"] for b in bel], 0.4, label="sekundär")
axs[1].set_ylabel("Strangspannung $U$ [V]")
for a in axs:
    a.set_xticks(x, namen, fontsize=8)
    a.legend(fontsize=8, loc="lower right")
fig.tight_layout()
fig.savefig(AUS / "belastung.pdf")
plt.close(fig)

# --------------------------------------------------------- Einschaltstrom
out("=== Einschaltstrom (Rush) ===")
fig, axs = plt.subplots(3, 1, figsize=(7.0, 7.0), sharex=True)
for a, name in zip(axs, ["scope_3.csv", "scope_6.csv", "scope_7.csv"]):
    d = np.genfromtxt(DATEN / name, delimiter=",", skip_header=2)
    m = ~np.isnan(d).any(axis=1)
    t, u, i = d[m, 0] * 1e3, d[m, 1], d[m, 2]
    a.plot(t, i, color="tab:blue", lw=0.8, label="$i_1$")
    a.set_ylabel("Strom $i_1$ [A]")
    a2 = a.twinx()
    a2.plot(t, u, color="tab:red", lw=0.8, label="$u_1$")
    a2.set_ylabel("Spannung $u_1$ [V]")
    a.set_title(name.replace(".csv", ""), fontsize=10)
    spitzen = []
    for p in range(10):
        s = (t >= -20.6 + 20 * p) & (t < -20.6 + 20 * (p + 1))
        if s.any():
            spitzen.append(i[s].min())
    k = np.argmin(i)
    out(f"{name}: i_max = {i[k]:.1f} A bei t = {t[k]:.2f} ms (u = {u[k]:.1f} V); "
        f"Spitzen je Periode: " + ", ".join(f"{abs(x):.0f}" for x in spitzen))
    out(f"   bezogen auf Nennstromscheitel {np.sqrt(2)*I_N_STR:.1f} A: "
        f"{abs(i[k])/(np.sqrt(2)*I_N_STR):.2f}-fach, auf Leerlaufstromscheitel "
        f"{np.sqrt(2)*I0N:.2f} A: {abs(i[k])/(np.sqrt(2)*I0N):.0f}-fach")
axs[-1].set_xlabel("Zeit $t$ [ms]")
fig.tight_layout()
fig.savefig(AUS / "rush.pdf")
plt.close(fig)

(AUS / "kennwerte.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
