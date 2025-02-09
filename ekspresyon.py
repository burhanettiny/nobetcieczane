import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# Başlık
st.title("Gen Ekspresyon Analizi Uygulaması")
st.markdown("### B. Yalçınkaya tarafından geliştirildi")

# Kullanıcıdan giriş al
st.header("Hasta ve Kontrol Grubu Verisi Girin")

# Hedef Gen Sayısı
num_target_genes = st.number_input("Hedef Gen Sayısını Girin", min_value=1, step=1)

data = []
stats_data = []
input_values_table = []

# Verileri işleyen fonksiyon
def parse_input_data(input_data):
    values = [x.replace(",", ".").strip() for x in input_data.split() if x.strip()]
    return np.array([float(x) for x in values if x])

for i in range(num_target_genes):
    st.subheader(f"Hedef Gen {i+1}")
    
    control_target_ct = st.text_area(f"Kontrol Grubu Hedef Gen {i+1} Ct Değerleri", key=f"control_target_ct_{i}")
    control_reference_ct = st.text_area(f"Kontrol Grubu Referans Gen {i+1} Ct Değerleri", key=f"control_reference_ct_{i}")
    sample_target_ct = st.text_area(f"Hasta Grubu Hedef Gen {i+1} Ct Değerleri", key=f"sample_target_ct_{i}")
    sample_reference_ct = st.text_area(f"Hasta Grubu Referans Gen {i+1} Ct Değerleri", key=f"sample_reference_ct_{i}")
    
    # Verileri kontrol et ve eksik veri varsa hata mesajı göster
    if not (control_target_ct and control_reference_ct and sample_target_ct and sample_reference_ct):
        st.error("Hata: Tüm veriler girilmelidir! Lütfen eksik veri bırakmayın.")
        continue
    
    control_target_ct_values = parse_input_data(control_target_ct)
    control_reference_ct_values = parse_input_data(control_reference_ct)
    sample_target_ct_values = parse_input_data(sample_target_ct)
    sample_reference_ct_values = parse_input_data(sample_reference_ct)
    
    # Verileri boyutlarını kontrol et
    if len(control_target_ct_values) != len(control_reference_ct_values):
        st.error("Hata: Kontrol Grubu Hedef Gen ve Referans Gen sayıları eşleşmiyor!")
        continue
    if len(sample_target_ct_values) != len(sample_reference_ct_values):
        st.error("Hata: Hasta Grubu Hedef Gen ve Referans Gen sayıları eşleşmiyor!")
        continue

    # ΔCt hesaplaması
    control_delta_ct = control_target_ct_values - control_reference_ct_values
    sample_delta_ct = sample_target_ct_values - sample_reference_ct_values

    # Boyutları kontrol et
    if control_delta_ct.shape != sample_delta_ct.shape:
        st.error("Hata: ΔCt hesaplaması için kontrol ve hasta grubu boyutları eşleşmiyor!")
        continue
    
    # Ortalamaları hesapla
    average_control_delta_ct = np.mean(control_delta_ct)
    average_sample_delta_ct = np.mean(sample_delta_ct)
    
    delta_delta_ct = average_sample_delta_ct - average_control_delta_ct
    expression_change = 2 ** (-delta_delta_ct)
    
    if expression_change == 1:
        regulation_status = "Değişim Yok"
    elif expression_change > 1:
        regulation_status = "Upregulated"
    else:
        regulation_status = "Downregulated"
    
    # Normallik testleri
    shapiro_control = stats.shapiro(control_delta_ct)
    shapiro_sample = stats.shapiro(sample_delta_ct)
    
    control_normal = shapiro_control.pvalue > 0.05
    sample_normal = shapiro_sample.pvalue > 0.05
    
    # Varyans testi
    levene_test = stats.levene(control_delta_ct, sample_delta_ct)
    equal_variance = levene_test.pvalue > 0.05
    
    # İstatistiksel test seçimi
    if control_normal and sample_normal and equal_variance:
        test_name = "T-Test"
        test_stat, test_pvalue = stats.ttest_ind(control_delta_ct, sample_delta_ct)
    else:
        test_name = "Mann-Whitney U"
        test_stat, test_pvalue = stats.mannwhitneyu(control_delta_ct, sample_delta_ct)
    
    # Güncellenmiş ternary ifade
    significance = "Anlamlı" if test_pvalue < 0.05 else "Anlamsız"
    
    # Append the statistical results to stats_data
    stats_data.append({
        "Hedef Gen": f"Hedef Gen {i+1}",
        "Normalite Testi Kontrol Grubu (Shapiro P-value)": shapiro_control.pvalue,
        "Normalite Testi Hasta Grubu (Shapiro P-value)": shapiro_sample.pvalue,
        "Varyans Testi (Levene P-value)": levene_test.pvalue,
        "Test Adı": test_name,
        "Test İstatistiği": test_stat,
        "Test P-değeri": test_pvalue,
        "Anlamlılık": significance
    })
    
    data.append({
        "Hedef Gen": f"Hedef Gen {i+1}",
        "Kontrol ΔCt (Ortalama)": average_control_delta_ct,
        "Hasta ΔCt (Ortalama)": average_sample_delta_ct,
        "ΔΔCt": delta_delta_ct,
        "Gen Ekspresyon Değişimi (2^(-ΔΔCt))": expression_change,
        "Regülasyon Durumu": regulation_status,
        "Kontrol Grubu Örnek Sayısı": len(control_target_ct_values),
        "Hasta Grubu Örnek Sayısı": len(sample_target_ct_values)
    })
    
    # Her örnek için sıra numarası ver
    for j in range(max(len(control_target_ct_values), len(sample_target_ct_values))):
        row = {"Hedef Gen": f"Hedef Gen {i+1}", "Örnek No": j+1}
        row["Kontrol Hedef Ct"] = control_target_ct_values[j] if j < len(control_target_ct_values) else np.nan
        row["Kontrol Referans Ct"] = control_reference_ct_values[j] if j < len(control_reference_ct_values) else np.nan
        row["Hasta Hedef Ct"] = sample_target_ct_values[j] if j < len(sample_target_ct_values) else np.nan
        row["Hasta Referans Ct"] = sample_reference_ct_values[j] if j < len(sample_reference_ct_values) else np.nan
        input_values_table.append(row)

# Giriş verileri tablosunu göster
st.subheader("Giriş Verileri Tablosu")
input_df = pd.DataFrame(input_values_table)
st.write(input_df)

# Sonuçları göster
st.subheader("Sonuçlar")
df = pd.DataFrame(data)
st.write(df)

# İstatistik Sonuçları
st.subheader("İstatistik Sonuçları")
stats_df = pd.DataFrame(stats_data)
st.write(stats_df)
