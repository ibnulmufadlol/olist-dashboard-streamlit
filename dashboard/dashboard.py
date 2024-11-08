import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import st_folium
from babel.numbers import format_currency
from datetime import datetime, date
import json
sns.set(style='dark')

# create function to prepare dataframe
def create_rfm_df(df):
    viz_rfm_df = df.groupby(by="customer_state", as_index=False).agg({
        "order_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    viz_rfm_df.columns = ["customer_state", "max_order_timestamp", "frequency", "monetary"]
    
    viz_rfm_df["max_order_timestamp"] = viz_rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    viz_rfm_df["recency"] = viz_rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    viz_rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return viz_rfm_df

def create_late_orders_df(df):
    late_orders_df = orders_df[orders_df['order_delivered_customer_date'] > orders_df['order_estimated_delivery_date']]
    return late_orders_df

def create_late_orders_area(df1, df2):
    late_orders_area = pd.merge(
        left=df1,
        right=df2,
        how="left",
        right_on="customer_id",
        left_on="customer_id"
    )
    return late_orders_area

def create_monthly_orders(df):
    df['order_date'] = df['order_date'].apply(pd.to_datetime)
    monthly_order_volume = df.groupby(df['order_date']
                                      .dt
                                      .to_period("M")
                                     )['order_id'].count()
    return monthly_order_volume

def create_payment_method_count(df):
    payment_type_counts = df.groupby('payment_type')['order_id'].nunique()
    return payment_type_counts

def create_order_reviews_df(df):
    review_score_count = df.groupby('review_score')['order_id'].nunique()
    return review_score_count

def create_order_reviews_detail(df):
    low_score_reviews = df[df['review_score'].isin([1, 2])]
    order_reviews_comment_detail = low_score_reviews[['review_comment_title', 'review_comment_message']]
    order_reviews_comment_detail = order_reviews_comment_detail.dropna(subset=['review_comment_message', 'review_comment_title'])
    return order_reviews_comment_detail

def create_product_category_df(df):
    category_order_counts_per_year = (df
                                  .groupby(['product_category', 'year'])
                                  .size()
                                  .reset_index(name='order_count')
                                  .sort_values(by=['product_category', 'year']))

    top_categories_per_year = (category_order_counts_per_year
                               .sort_values(['year', 'order_count'], ascending=[True, False])
                               .groupby('year')
                               .head(5))  # kita pilih 5 saja per tahun
    top_categories_per_year['year'] = top_categories_per_year['year'].astype(int)
    return top_categories_per_year

def create_customer_per_state(df):
    customer_per_state = df.groupby('customer_state')['customer_id'].nunique()
    return customer_per_state

# load dataset
rfm_df = pd.read_csv("rfm_data.csv")
rfm_df["order_date"] = pd.to_datetime(rfm_df["order_date"])

orders_df = pd.read_csv("order_details.csv")
orders_df[["order_approved_at", "order_delivered_customer_date", "order_estimated_delivery_date"]] = orders_df[["order_approved_at", "order_delivered_customer_date", "order_estimated_delivery_date"]].apply(pd.to_datetime)
orders_df.loc[:, 'order_date'] = orders_df['order_approved_at'].dt.date
orders_df = orders_df.drop(columns=['order_approved_at'])
orders_df['year'] = pd.to_datetime(orders_df['order_date']).dt.year

customers_df = pd.read_csv("customers.csv")

product_category_df = pd.read_csv("order_prod_category.csv")

with open('brazil_geo.json') as f:
    geojson_data = json.load(f)
    for feature in geojson_data['features']:
        feature['properties']['id'] = feature['id']
# sidebar
min_date = rfm_df["order_date"].min().date()
max_date = rfm_df["order_date"].max().date()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("Logo-Olist-1.png")
    st.title('Filter(s)')
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(label='Periode Order', min_value=min_date, max_value=max_date, value=[min_date, max_date])

# implement filter tanggal
filtered_rfm_df = rfm_df[(rfm_df["order_date"] >= str(start_date)) & 
                (rfm_df["order_date"] <= str(end_date))]
filtered_orders_df = orders_df[(orders_df["order_date"] >= start_date) & 
                (orders_df["order_date"] <= end_date)]

# prepare viz dataframe
viz_rfm_df = create_rfm_df(filtered_rfm_df)
late_orders_df = create_late_orders_df(filtered_orders_df)
late_orders_area = create_late_orders_area(filtered_orders_df, customers_df)
monthly_order_volume = create_monthly_orders(filtered_orders_df)
payment_type_counts = create_payment_method_count(filtered_orders_df)
review_score_count = create_order_reviews_df(filtered_orders_df)
order_reviews_comment_detail = create_order_reviews_detail(filtered_orders_df)
top_categories_per_year = create_product_category_df(product_category_df)
customer_per_state = create_customer_per_state(customers_df)

st.header("Olist: E-Commerce Collection Dashboard")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["RFM Analysis", "Best Product Category", "SLA Monitoring", "Orders", "Payment Method", "Order Reviews"])

with tab1:
    st.subheader("Best States Based on RFM Parameters")

    t1_col1, t1_col2, t1_col3 = st.columns(3)
    
    with t1_col1:
        avg_recency = round(viz_rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
    
    with t1_col2:
        avg_frequency = round(viz_rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
    
    with t1_col3:
        avg_monetary = format_currency(viz_rfm_df.monetary.mean(), "BRL", locale='es_CO') 
        st.metric("Average Monetary", value=avg_monetary)
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
    
    sns.barplot(y="recency", x="customer_state", data=viz_rfm_df.sort_values(by="recency", ascending=True).head(5), ax=ax[0])
    ax[0].set_ylabel("Hari")
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (Hari)", loc="center", fontsize=18)
    ax[0].tick_params(axis='x', labelsize=20)
    
    sns.barplot(y="frequency", x="customer_state", data=viz_rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
    ax[1].set_ylabel("Order Quantity")
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=20)
    
    sns.barplot(y="monetary", x="customer_state", data=viz_rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])
    ax[2].set_ylabel("BRL (dalam Jutaan)")
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary (Juta)", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=20)
    
    plt.suptitle("Best State Based on RFM Parameters (customer_state)", fontsize=30)
    
    st.pyplot(fig)

    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)
    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=customer_per_state,
        columns=["customer_state", "customer_id"],
        key_on="feature.id",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Jumlah Pelanggan per Negara Bagian"
    ).add_to(m)
    folium.GeoJson(
        data=geojson_data,
        style_function=lambda x: {'fillColor': 'transparent', 'color': 'transparent'},
        tooltip=folium.GeoJsonTooltip(
            fields=['id', 'name'],  # 'id' and 'name' fields in GeoJSON properties
            aliases=['State ID:', 'State Name:'],  # Labels for tooltip
            localize=True
        )
    ).add_to(m)
    
    st.title("Peta Area Pelanggan Terbanyak di Brazil")
    st_folium(m, width=700, height=500)

with tab2:
    st.subheader("Product Category Monitoring")
    st.error("Attention: This tab is not affected by filter(s)")
    unique_years = top_categories_per_year['year'].unique()
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 8))

    for i, year in enumerate(unique_years):
        yearly_data = top_categories_per_year[top_categories_per_year['year'] == year]
        axs[i].bar(yearly_data['product_category'], yearly_data['order_count'], color='skyblue')
        axs[i].set_title(f'Top 5 Product Categories in {year}')
        axs[i].set_xlabel('Product Category')
        axs[i].set_ylabel('Quantity')
        axs[i].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)

with tab3:
    st.subheader("SLA Monitoring for Late Orders Delivery")

    t3_col1, t3_col2 = st.columns(2)
    
    with t3_col1:
        late_order_count = late_orders_df['order_id'].nunique()
        st.metric("Orders Over SLA", value=late_order_count)

    with t3_col2:
        late_orders_modify = late_orders_df.copy()
        late_orders_modify['late_days'] = (
            late_orders_modify['order_delivered_customer_date'] - late_orders_modify['order_estimated_delivery_date']
        ).dt.days
        average_late_days = round(late_orders_modify['late_days'].mean(), 2)
        st.metric("Average Over Time (days)", value=average_late_days)

    late_order_states = (late_orders_area['customer_state']
                         .value_counts()
                         .head())

    fig, ax = plt.subplots(figsize=(10, 6))
    late_order_states.plot(kind='bar', ax=ax)
    
    ax.set_title("Top 5 States with Late Orders Delivery")
    ax.set_xlabel("Negara Bagian")
    ax.set_ylabel("Quantity")
    ax.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)

with tab4:
    # Menemukan bulan dengan volume pesanan tertinggi dan terendah
    highest_volume_month = monthly_order_volume.idxmax()
    lowest_volume_month = monthly_order_volume.idxmin()
    highest_volume_value = monthly_order_volume.max()
    lowest_volume_value = monthly_order_volume.min()
    # Create a line chart in Streamlit
    st.title("Monthly Order Volume")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_order_volume.plot(kind='line', color='blue', label='Monthly Order Volume', ax=ax)
    
    # Mark the highest and lowest volume months
    ax.scatter(
        [highest_volume_month.to_timestamp()], 
        [highest_volume_value], 
        color='green', 
        label=f'Highest: {highest_volume_month} ({highest_volume_value})'
    )
    ax.scatter(
        [lowest_volume_month.to_timestamp()], 
        [lowest_volume_value], 
        color='red', 
        label=f'Lowest: {lowest_volume_month} ({lowest_volume_value})'
    )
    
    ax.set_title('Monthly Order Volume')
    ax.set_xlabel('Month')
    ax.set_ylabel('Order Quantity')
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Render the plot in Streamlit
    st.pyplot(fig)

with tab5:
    st.title("Payment Methods Monitoring")

    fig, ax = plt.subplots(figsize=(10, 6))
    payment_type_counts.plot(kind='bar', ax=ax)
    
    ax.set_title('Frequent Used Payment Methods')
    ax.set_xlabel('Payment Methods')
    ax.set_ylabel('Quantity')
    ax.tick_params(axis='x', rotation=45)
    
    st.pyplot(fig)

with tab6:
    st.title("Order Reviews Monitoring")

    fig, ax = plt.subplots(figsize=(10, 6))
    review_score_count.plot(kind='bar', ax=ax)
    
    ax.set_title('Order Reviews Score')
    ax.set_xlabel('Review Score')
    ax.set_ylabel('Quantity')
    ax.tick_params(axis='x', rotation=0)
    
    st.pyplot(fig)

    st.text("Table: Detail Review's Comment")
    st.dataframe(order_reviews_comment_detail, width=1000, height=400)

# Display the footer on all tabs
current_year = datetime.now().year
st.caption("Copyright (c) Ibnul Mufadlol ", current_year)