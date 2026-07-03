import serial
import re
import time
import subprocess

COM_PORT   = 'COM6'
BAUD_RATE  = 115200
MAX_SAMPLE = 60
GNUPLOT    = r"C:\Program Files\gnuplot\bin\gnuplot.exe"

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=2)
    print(f"[OK] Serial {COM_PORT} terbuka")
except Exception as e:
    print(f"[ERROR] {e}"); exit(1)

try:
    gp = subprocess.Popen(
        [GNUPLOT],
        stdin=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    print("[OK] GNUPlot berjalan")
except Exception as e:
    print(f"[ERROR] {e}"); ser.close(); exit(1)

def gp_send(cmd):
    try:
        gp.stdin.write(cmd + "\n")
        gp.stdin.flush()
    except:
        pass

# ============================================================
# KALIBRASI AWAL — Ambil 5 data valid untuk benchmark Angka 0
# ============================================================
print("[WAIT] Mengumpulkan 5 data awal untuk kalibrasi Titik Nol yang stabil...")

startup_samples = []
while len(startup_samples) < 5:
    try:
        raw  = ser.readline()
        line = raw.decode(errors='ignore').strip()
        if not line.startswith("TEMP="):
            continue

        t  = re.search(r"TEMP=([0-9.]+)",  line)
        h  = re.search(r"HUM=([0-9.]+)",   line)
        mo = re.search(r"MOIST=([0-9.]+)", line)
        co = re.search(r"CO2=([0-9.]+)",   line)
        cs = re.search(r"CSRI=([0-9.]+)",  line)

        if all([t, h, mo, co, cs]):
            startup_samples.append({
                'temp' : float(t.group(1)),
                'hum'  : float(h.group(1)),
                'moist': float(mo.group(1)),
                'co2'  : float(co.group(1)),
                'csri' : float(cs.group(1)),
            })
            print(f"[INFO] Mengkalibrasi... ({len(startup_samples)}/5)")
    except:
        pass

# Hitung rata-rata data awal agar titik 0 tidak loncat rusak
relative_base = {
    'temp' : sum(d['temp'] for d in startup_samples) / 5,
    'hum'  : sum(d['hum'] for d in startup_samples) / 5,
    'moist': sum(d['moist'] for d in startup_samples) / 5,
    'co2'  : sum(d['co2'] for d in startup_samples) / 5,
    'csri' : sum(d['csri'] for d in startup_samples) / 5,
}
print(f"[OK] Kalibrasi Sukses! Baseline Nol dikunci.")

# ============================================================
# SETUP GNUPLOT
# ============================================================
gp_send("set terminal wxt size 1100,600 title 'Smart Grain Storage (Kompak dari 0)' enhanced persist")
gp_send("set xlabel 'Sample (1 detik/sample)'")
gp_send("set ylabel 'Deviasi Nilai (Mulai dari 0)'")
gp_send("set xrange [0:60]")
gp_send("set yrange [-15:15]") # Membatasi rentang Y agar pergerakan terlihat rapi dan tidak berantakan
gp_send("set grid")
gp_send("set key top right outside")

# Warna garis pelangi tebal
gp_send("set style line 1 lc rgb '#E41A1C' lw 3") # Temp (Merah)
gp_send("set style line 2 lc rgb '#377EB8' lw 3") # Humidity (Biru)
gp_send("set style line 3 lc rgb '#4DAF4A' lw 3") # Moisture (Hijau)
gp_send("set style line 4 lc rgb '#FF7F00' lw 3") # CO2 (Orange)
gp_send("set style line 5 lc rgb '#984EA3' lw 3") # CSRI (Ungu)

# ============================================================
# BUFFER DATA
# ============================================================
data = {'temp': [], 'hum': [], 'moist': [], 'co2': [], 'csri': []}
sample_num = 0

print("[OK] Mulai plotting...")
print("-" * 60)

# ============================================================
# LOOP UTAMA
# ============================================================
while True:
    try:
        raw  = ser.readline()
        if not raw:
            continue

        line = raw.decode(errors='ignore').strip()
        if not line or not line.startswith("TEMP="):
            continue

        t  = re.search(r"TEMP=([0-9.]+)",  line)
        h  = re.search(r"HUM=([0-9.]+)",   line)
        mo = re.search(r"MOIST=([0-9.]+)", line)
        co = re.search(r"CO2=([0-9.]+)",   line)
        cs = re.search(r"CSRI=([0-9.]+)",  line)

        if not all([t, h, mo, co, cs]):
            continue

        # Data Asli dari Sensor
        raw_temp  = float(t.group(1))
        raw_hum   = float(h.group(1))
        raw_moist = float(mo.group(1))
        raw_co2   = float(co.group(1))
        raw_csri  = float(cs.group(1))

        # Pengurangan dengan baseline stabil (Mulai dari 0)
        plot_temp  = raw_temp - relative_base['temp']
        plot_hum   = raw_hum - relative_base['hum']
        plot_moist = raw_moist - relative_base['moist']
        plot_co2   = raw_co2 - relative_base['co2']
        plot_csri  = raw_csri - relative_base['csri']

        # Masukkan ke buffer
        data['temp'].append(plot_temp)
        data['hum'].append(plot_hum)
        data['moist'].append(plot_moist)
        data['co2'].append(plot_co2)
        data['csri'].append(plot_csri)

        if len(data['temp']) > MAX_SAMPLE:
            for key in data:
                data[key].pop(0)

        sample_num += 1

        # Hitung pergeseran Sumbu X
        n = len(data['temp'])
        if sample_num <= MAX_SAMPLE:
            x_start = 0
            x_end = MAX_SAMPLE
            xs = list(range(n))
        else:
            x_start = sample_num - MAX_SAMPLE
            x_end = sample_num
            xs = list(range(x_start, x_start + n))

        gp_send(f"set xrange [{x_start}:{x_end}]")

        # Cetak teks ke terminal monitor
        print(f"  [#{sample_num}] T={raw_temp:.1f}°C H={raw_hum:.1f}% M={raw_moist:.0f}% CO2={raw_co2:.0f} CSRI={raw_csri:.1f}")

        # Update Judul Grafis Atas dengan Nilai Asli Aktual
        gp_send(f"set title 'Smart Storage Realtime | T={raw_temp:.1f}C  H={raw_hum:.1f}%  M={raw_moist:.0f}%  CO2={raw_co2:.0f}  CSRI={raw_csri:.1f}'")

        # Plot ulang data ke Gnuplot
        gp_send(
            "plot "
            "'-' with lines ls 1 title 'Temp (Δ)', "
            "'-' with lines ls 2 title 'Humidity (Δ)', "
            "'-' with lines ls 3 title 'Moisture (Δ)', "
            "'-' with lines ls 4 title 'CO2 (Δ)', "
            "'-' with lines ls 5 title 'CSRI (Δ)'"
        )

        for key in ['temp', 'hum', 'moist', 'co2', 'csri']:
            for x, v in zip(xs, data[key]):
                gp_send(f"{x} {float(v):.2f}")
            gp_send("e")

    except KeyboardInterrupt:
        print("\n[STOP] Dihentikan oleh user.")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(0.1)

# Cleanup
try:
    gp_send("quit")
    gp.stdin.close()
except:
    pass
ser.close()
print("[DONE]")