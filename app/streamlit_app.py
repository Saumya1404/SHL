import streamlit as st
import requests

API_URL = "https://shl-5osm.onrender.com/"

st.set_page_config(page_title="SHL Recommender", layout="wide")
st.title("SHL Assessment Recommender")

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Retrieval top_k", min_value=5, max_value=200, value=50)
    final_k = st.slider("Final recommendations (k)", min_value=1, max_value=20, value=5)

st.write("Enter a job description, role, or short query and click **Recommend**.")
query = st.text_area("Query / Job Description", height=200)

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a query or job description.")
    else:
        with st.spinner("Generating recommendations..."):
            try:
                payload = {
                    "query": query,
                    "top_k": top_k,
                    "final_k": final_k
                }
                response = requests.post(
                    f"{API_URL}/recommend",
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("recommended_assessments", [])
            except Exception as e:
                st.error(f"Failed to fetch recommendations: {e}")
                results = []

        if not results:
            st.info("No recommendations found.")
        else:
            st.success(f"Found {len(results)} recommendation(s)")
            for i, r in enumerate(results, 1):
                st.markdown(f"### {i}. {r.get('name') or r.get('url')}")

                cols = st.columns([3, 1, 1])

                with cols[0]:
                    if r.get("description"):
                        st.write(r["description"])
                    if r.get("url"):
                        st.markdown(f"**URL:** [{r['url']}]({r['url']})")

                with cols[1]:
                    st.write(f"**Type:** {r.get('test_type', '—')}")

                with cols[2]:
                    st.write(f"**Duration:** {r.get('duration', '—')}")

st.markdown("---")

