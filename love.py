import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

# Load the Excel data
data = pd.read_excel('love.xlsx', engine='openpyxl')

# Convert Date column to datetime format and create year and month features
data['Date'] = pd.to_datetime(data['Date'])
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month

# Define target-influential state pairs
state_pairs = {
    'Arunachal Pradesh': 'Bihar',
    'Orissa': 'Andhra Pradesh',
    'Jharkhand': 'Bihar',
    'Bihar': 'Jharkhand',
    'West Bengal': 'Jharkhand',
    'Nagaland': 'Andhra Pradesh',
    'Sikkim': 'Arunachal Pradesh',
    'Assam & Meghalaya': 'Nagaland',
    'Andaman & Nicobar Islands': 'Tamil Nadu',
    'Uttar Pradesh': 'Haryana Delhi & Chandigarh',
    'Uttarakhand': 'Himachal Pradesh',
    'Haryana Delhi & Chandigarh': 'Himachal Pradesh',
    'Punjab': 'Rajasthan',
    'Himachal Pradesh': 'Jammu & Kashmir',
    'Jammu & Kashmir': 'Himachal Pradesh',
    'Rajasthan': 'Punjab',
    'Madhya Pradesh': 'Gujarat',
    'Gujarat': 'Rajasthan',
    'Goa': 'Karnataka',
    'Lakshadweep': 'Kerala',
    'Chhattisgarh': 'Telangana',
    'Andhra Pradesh': 'Tamil Nadu',
    'Telangana': 'Andhra Pradesh',
    'Tamil Nadu': 'Kerala',
    'Karnataka': 'Andhra Pradesh',
    'Kerala': 'Lakshadweep',
    'Maharashtra': 'Gujarat',
}

# Streamlit App
st.title("Praveen's Rainfall Prediction Tool")

# Check if dark mode is enabled using Streamlit's theme settings
dark_mode = st.get_option("theme.base") == "dark"

# Define text colors based on mode
text_color = "#FFFFFF" if dark_mode else "#000000"

# Apply styles for text color
def style_text(text):
    return f"<span style='color: {text_color};'>{text}</span>"

# Select target state
target_state = st.selectbox("Select the target state you want to predict rainfall for:", options=list(state_pairs.keys()))
influential_state = state_pairs.get(target_state)

if influential_state:
    st.write(f"Using **{influential_state}** as the influential state for **{target_state}**.")


    # Prepare data for prediction
    data['Next_Month_Value'] = data[target_state].shift(-1)
    data['Next_Month'] = data['Date'].shift(-1).dt.month
    data['Next_Year'] = data['Date'].shift(-1).dt.year
    data['Is_Consecutive'] = (
        ((data['Month'] + 1) % 12 == data['Next_Month']) &
        ((data['Month'] == 12) & (data['Next_Year'] == data['Year'] + 1) |
         (data['Month'] != 12) & (data['Next_Year'] == data['Year']))
    )
    valid_pairs = data[data['Is_Consecutive']]

    # Prepare data for Linear Regression
    X = valid_pairs[['Month', influential_state]]
    y = valid_pairs['Next_Month_Value']
    model = LinearRegression()
    model.fit(X, y)

    # Month selection and input for influential state
    month_mapping = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }
    input_month = st.selectbox(f"Select the current month of {influential_state}:", list(month_mapping.keys()))
    month_num = month_mapping[input_month]
    random_value = st.number_input(f"Enter rainfall value for {influential_state} in {input_month}:", min_value=0.0)

    # Define background images based on predicted rainfall
    def set_background(image_url):
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url({image_url});
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

    # Predict the next month's value for the target state
    if st.button("Predict Next Month's Rainfall"):
        predicted_value = max(model.predict([[month_num, random_value]])[0], 0)
        next_month_num = (month_num % 12) + 1
        reverse_month_mapping = {v: k for k, v in month_mapping.items()}
        next_month = reverse_month_mapping[next_month_num]

        # Display the prediction with styled text
        # Using st.write for automatic theme adaptation
        # Using st.markdown without explicit font size, following the theme
        st.markdown(
             f"<p style='color: var(--text-color);'>{f'The predicted rainfall for {target_state} in {next_month} is: {predicted_value:.2f} mm'}</p>",
             unsafe_allow_html=True
        )



        # Set background image based on the predicted rainfall
        if predicted_value < 200:
            set_background("https://www.cleveland.com/resizer/v2/7TPNT3GG5ZBRXMY7DBJGGPS7EQ.jpg?auth=6a39dd4b9695c068dc473109cc5da36edd2bd09c6702f631af97223762bd458c&width=1280&quality=90")
        elif predicted_value > 500:
            set_background("https://cdn.labmanager.com/assets/articleNo/31834/aImg/56785/air-pollution-hides-increases-in-rainfall-m.webp")
        else:
            set_background("https://s.w-x.co/util/image/w/in-mumbai_rain_0.jpg?width=980")
else:
    st.markdown(style_text("No influential state found for the selected target state. Please choose another state."), unsafe_allow_html=True)

