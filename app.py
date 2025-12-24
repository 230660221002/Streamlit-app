# ==========================
# DASHBOARD ANALISIS REVIEW PRODUK (Dengan Heatmap Korelasi)
# ==========================

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# 1. DATASET
# ----------------------------
# Load the new dataset
df = pd.read_csv('tokopedia-product-reviews-2019.csv')

# Drop the 'Unnamed: 0' column if it exists
if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

# Convert 'sold' to numeric, coercing errors to NaN and filling NaN with 0
df['sold'] = pd.to_numeric(df['sold'], errors='coerce').fillna(0).astype(int)

# Ensure 'rating' is integer
df['rating'] = df['rating'].astype(int)

# ----------------------------
# 2. DESAIN DASBOR
# ----------------------------
st.set_page_config(
    page_title="Dashboard Analisis Review Produk",
    layout="wide"
)

st.title(" Dashboard Analisis Review Produk Tokopedia")
st.markdown("Selamat datang di dashboard analisis review produk interaktif. Gunakan filter di samping untuk menjelajahi data berdasarkan rating, kategori, ID toko, dan nama produk.")


# ----------------------------
# 3. SIDEBAR FILTER
# ----------------------------
st.sidebar.header(" Filter Data")

# New filters for the product review data
rating_options = sorted(df["rating"].unique(), reverse=True)
rating_filter = st.sidebar.multiselect(
    "Pilih Rating",
    options=rating_options,
    default=rating_options
)

category_options = sorted(df["category"].unique())
category_filter = st.sidebar.multiselect(
    "Pilih Kategori",
    options=category_options,
    default=category_options
)

shop_id_options = sorted(df["shop_id"].unique().astype(str))
shop_id_filter = st.sidebar.multiselect(
    "Pilih ID Toko",
    options=shop_id_options,
    default=shop_id_options[:10] # Default to top 10 for performance
)

product_name_search = st.sidebar.text_input(
    "Cari Nama Produk (ketik untuk filter)"
)

# Apply filters
df_filtered = df[
    (df["rating"].isin(rating_filter)) &
    (df["category"].isin(category_filter)) &
    (df["shop_id"].astype(str).isin(shop_id_filter))
]

# Apply product name search filter
if product_name_search:
    df_filtered = df_filtered[df_filtered["product_name"].str.contains(product_name_search, case=False, na=False)]


# ----------------------------
# 4. KPI CARDS
# ----------------------------
st.subheader(" Key Performance Indicators")

total_reviews = len(df_filtered)
if not df_filtered.empty:
    average_rating = df_filtered["rating"].mean()
    most_reviewed_product = df_filtered["product_name"].mode()[0]
else:
    average_rating = 0
    most_reviewed_product = "N/A"

col1, col2, col3 = st.columns(3)
col1.metric("Total Ulasan", f"{total_reviews:,}")
col2.metric("Rating Rata-rata", f"{average_rating:,.2f}")
col3.metric("Produk Paling Banyak Diulas", most_reviewed_product)


# ----------------------------
# 5. TABS
# ----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" Distribusi Rating", " Top Kategori", " Rating per Kategori", " Line Chart Distribusi Rating", " Data Table", " Statistik"]) # Updated tab titles


# --- TAB 1 Distribusi Rating (Bar Chart) ---
with tab1:
    st.subheader("Distribusi Rating (Bar Chart)")

    if not df_filtered.empty:
        rating_counts = df_filtered['rating'].value_counts().sort_index().reset_index()
        rating_counts.columns = ['Rating', 'Jumlah Ulasan']
        fig_rating_bar = px.bar(
            rating_counts,
            x="Rating",
            y="Jumlah Ulasan",
            title="Distribusi Jumlah Ulasan Berdasarkan Rating"
        )
        st.plotly_chart(fig_rating_bar, use_container_width=True)
    else:
        st.warning("Tidak ada data rating yang tersedia untuk ditampilkan berdasarkan filter.")


# --- TAB 2 Top Kategori ---
with tab2:
    st.subheader("Top Kategori Berdasarkan Jumlah Ulasan")

    if not df_filtered.empty:
        category_counts = df_filtered['category'].value_counts().head(10).reset_index()
        category_counts.columns = ['Kategori', 'Jumlah Ulasan']
        fig_category = px.bar(
            category_counts,
            x="Jumlah Ulasan",
            y="Kategori",
            orientation='h',
            title="Top 10 Kategori Paling Banyak Diulas"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.warning("Tidak ada data kategori yang tersedia untuk ditampilkan berdasarkan filter.")


# --- TAB 3 Rating per Kategori ---
with tab3:
    st.subheader("Rata-rata Rating berdasarkan Kategori Produk")

    if not df_filtered.empty:
        df_avg_rating_category = df_filtered.groupby('category')['rating'].mean().reset_index()
        df_avg_rating_category.columns = ['Kategori', 'Rata-rata Rating']
        fig_line_category = px.line(
            df_avg_rating_category,
            x="Kategori",
            y="Rata-rata Rating",
            markers=True,
            title="Rata-rata Rating Produk per Kategori"
        )
        st.plotly_chart(fig_line_category, use_container_width=True)
    else:
        st.warning("Tidak ada data rata-rata rating per kategori yang tersedia untuk ditampilkan berdasarkan filter.")

# --- TAB 4 Line Chart Distribusi Rating ---
with tab4:
    st.subheader("Distribusi Rating (Line Chart)")

    if not df_filtered.empty:
        rating_counts_line = df_filtered['rating'].value_counts().sort_index().reset_index()
        rating_counts_line.columns = ['Rating', 'Jumlah Ulasan']
        fig_rating_line = px.line(
            rating_counts_line,
            x="Rating",
            y="Jumlah Ulasan",
            title="Distribusi Jumlah Ulasan Berdasarkan Rating (Line Chart)",
            markers=True
        )
        st.plotly_chart(fig_rating_line, use_container_width=True)
    else:
        st.warning("Tidak ada data rating yang tersedia untuk ditampilkan berdasarkan filter.")


# --- TAB 5 Data Table ---
with tab5:
    st.subheader("Data Ulasan (Hasil Filter)")
    st.dataframe(df_filtered)

    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="data_ulasan_filtered.csv",
        mime="text/csv"
    )


# --- TAB 6 Statistik ---
with tab6:
    st.subheader(" Statistik Deskriptif")
    st.write(df_filtered.describe())

    st.subheader(" Heatmap Korelasi Antar Rating dan Jumlah Terjual")

    if not df_filtered.empty and len(df_filtered) > 1:
        # Calculate correlation for 'rating' and 'sold'
        corr_data = df_filtered[['rating', 'sold']]
        corr_matrix = corr_data.corr()

        # Plot heatmap with plotly
        fig_heat = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            title="Heatmap Korelasi Antara Rating dan Jumlah Terjual"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("Tidak cukup data untuk menghitung korelasi.")


# ----------------------------
# 6. FOOTER
# ----------------------------
st.markdown("---")
st.caption("Dashboard dibuat menggunakan **Streamlit**, **Pandas**, dan **Plotly** untuk menganalisis **ulasan produk**.")
