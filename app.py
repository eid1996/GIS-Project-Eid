import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import os, tempfile, io

# 1. إعدادات الصفحة والسايدبار 
st.set_page_config(page_title="GIS Project | Eid", layout="wide")

with st.sidebar:
    st.title("مشروع مادة تقنين وبرمجيات نظم المعلومات الجغرافية")
    st.write("إشراف المهندس محمد حبوب")
    st.write("عمل الطالب: عيد العكلوك")

st.markdown("<h1 style='text-align: center;'>التحليل المكاني والوصفي الذكية</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>إعداد الطالب: <b>عيد احمدرضا العكلوك</b> | الرقم الجامعي: 120182806</p>", unsafe_allow_html=True)

# 2. دالة تحميل البيانات
def load_data(uploaded_file):
    if uploaded_file:
        suffix = os.path.splitext(uploaded_file.name)[1]
        if uploaded_file.name.endswith('.geojson.txt'): suffix = '.geojson'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            path = tmp.name
        gdf = gpd.read_file(path)
        if gdf.crs is None: gdf.set_crs(epsg=4326, inplace=True)
        return gdf.to_crs(epsg=4326)
    return None

# 3. واجهة الرفع مع المعاينة 
st.header("1. رفع ومعاينة البيانات الجغرافية")
col1, col2 = st.columns(2)

with col1:
    st.subheader("الطبقة الأساسية")
    f1 = st.file_uploader("ارفع ملف GeoJSON (1)", key="u1")
    gdf1 = load_data(f1)
    if gdf1 is not None: 
        st.success("تم تحميل الطبقة الأولى")
        m1 = leafmap.Map(height=300)
        m1.add_gdf(gdf1)
        m1.to_streamlit()

with col2:
    st.subheader("الطبقة الثانوية")
    f2 = st.file_uploader("ارفع ملف GeoJSON (2)", key="u2")
    gdf2 = load_data(f2)
    if gdf2 is not None: 
        st.success("تم تحميل الطبقة الثانية")
        m2 = leafmap.Map(height=300)
        m2.add_gdf(gdf2)
        m2.to_streamlit()

# 4. إعدادات الربط والتنفيذ
if gdf1 is not None and gdf2 is not None:
    st.markdown("---")
    st.header("2. إعدادات عملية الربط")
    
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    
    with col_opt1:
        join_category = st.selectbox("اختر فئة الربط:", ["الربط المكاني (Spatial Join)", "الربط الوصفي (Attribute Join)"])
    
    with col_opt2:
        if "Spatial" in join_category:
            pred = st.selectbox("نوع العلاقة المكانية:", ["intersects", "contains", "within", "touches", "crosses"])
            how_type = "inner"
        else:
            l_col = st.selectbox("حقل الربط (الطبقة 1):", gdf1.columns)
            how_type = st.selectbox("حدد نوع الربط (Method):", ["inner", "left", "right", "outer"])

    with col_opt3:
        if "Attribute" in join_category:
            r_col = st.selectbox("حقل الربط (الطبقة 2):", gdf2.columns)
        else:
            st.info("الربط المكاني يعتمد على الموقع")

    if st.button(" تنفيذ عملية الربط الآن"):
        # تنفيذ العملية
        if "Spatial" in join_category:
            result = gpd.sjoin(gdf1, gdf2, how="inner", predicate=pred)
        else:
            result = gdf1.merge(gdf2.drop(columns='geometry', errors='ignore'), left_on=l_col, right_on=r_col, how=how_type)

        # 5. عرض النتائج (ثالثاً ورابعاً)
        if result is not None and len(result) > 0:
            st.markdown("---")
            st.header("3. مخرجات التحليل")
            
            # أ- عرض عدد الأسطر الناتجة (طلب المهندس)
            st.info(f" عدد الأسطر الناتجة من عملية الربط: {len(result)} سطر.")
            
            # ب- معاينة الخريطة النهائية
            st.subheader("معاينة الخريطة النهائية")
            m_res = leafmap.Map(height=400)
            m_res.add_gdf(result)
            m_res.to_streamlit()
            
            # ج- تنزيل النتائج (صيغة GeoJSON فقط - طلب المهندس)
            st.markdown("---")
            st.subheader("4. تنزيل النتائج")
            st.download_button(
                label=" تحميل النتيجة بصيغة GeoJSON",
                data=result.to_json(),
                file_name="Eid_Result.geojson",
                mime="application/json",
                use_container_width=True
            )
        else:
            # د- رسالة عدم وجود تطابق (طلب المهندس)
            st.error("⚠️ عذراً، لا توجد نتائج مطابقة لعملية الربط بناءً على الإعدادات المختارة.")