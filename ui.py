import streamlit as st
import pandas as pd
import pickle
from dateutil.relativedelta import relativedelta
import datetime
import plotly.graph_objects as go


def generate_predictions(model, start_date, end_date, date_difference):
    future_time_period = date_difference.months
    future_dates = [
        start_date + relativedelta(months=i) for i in range(0, future_time_period)]
    print(start_date, end_date, date_difference)
    print(future_dates)
    future_df = pd.DataFrame({'year': [d.year for d in future_dates], 'month': [
                             d.month for d in future_dates]})
    # Predict future prices
    # print(future_df)
    future_prices, conf_int = model.predict(
        future_time_period, return_conf_int=True)
    print(future_prices)
    conf_int_lower = [item[0] for item in conf_int]
    conf_int_upper = [item[1] for item in conf_int]
    # print(conf_int_upper)
    # print(future_prices)
    return pd.DataFrame({'Date': future_dates, 'Sugar Price': future_prices, 'Conf Int (Lower)': conf_int_lower, 'Conf Int (Upper)': conf_int_upper})


def create_line_chart_data(model, start_date, end_date, date_difference):
    historical_data = pd.read_csv(
        './final_sugar_price_forecasting_data.csv')[-23:]
    historical_data['Date'] = pd.to_datetime(historical_data['Date'])
    historical_data['Type'] = [
        'Historical' for x in range(len(historical_data))]
    predictions = generate_predictions(
        model, start_date, end_date, date_difference).round(2)
    predictions['Type'] = ['Predicted' for x in range(len(predictions))]
    predictions['Date'] = pd.to_datetime(predictions['Date'])
    final_data = pd.concat([historical_data, predictions], ignore_index=True).reset_index(
        drop=True).sort_values(by='Date')
    final_data = final_data.round(2)
    return final_data, predictions


# Title of the app/webapge
st.title("Indian Sugar Price Forecasting")


# Add buttons to select code type
st.sidebar.header("Forecasting Time Horizon")
code_type = st.sidebar.radio(
    "Select the time horizon for Sugar Price forecasts:",
    ("Short-term Forecast", "Long-term Forecast "),
    captions=[
        "( <= 6 months )",
        "( > 6 months )"
    ],
)


if code_type.lower() == "short-term forecast":
    selected_model = pickle.load(
        open('./short-term-forecasting-model.pkl', 'rb'))
else:
    selected_model = pickle.load(
        open('./long-term-forecasting-model.pkl', 'rb'))


st.sidebar.header("Select Date Range for Forecast")
start_date = st.sidebar.date_input(
    "Start Date", format="DD/MM/YYYY", value=datetime.date(2024, 12, 1))

if code_type.lower() == "short-term forecast":
    end_date = st.sidebar.date_input(
        "End Date", format="DD/MM/YYYY", value=datetime.date(2025, 2, 1), max_value=start_date+relativedelta(months=6))
else:
    end_date = st.sidebar.date_input(
        "End Date", format="DD/MM/YYYY", value=datetime.date(2025, 7, 1), min_value=start_date+relativedelta(months=7))
    # load the short-term forecasting model
    # time.sleep(2) # Wait for 2 seconds
    # alert.empty() # Clear the alert

date_difference = relativedelta(end_date, start_date)

if start_date >= end_date:
    st.error("Error: Start Date cannot be equal to or greater than End Date. Please change your dates!",
             icon=':material/error:')
else:
    # Generate data for the charts
    complete_data, predictions = create_line_chart_data(
        selected_model, start_date, end_date, date_difference)

    # # Display line charts
    st.subheader(f"Line Chart for prediction ({code_type})", divider=True)

    # Create a Plotly Figure
    fig = go.Figure()

    # Plot the combined line with color segmentation
    fig.add_trace(go.Scatter(
        x=complete_data['Date'],
        y=complete_data['Sugar Price'],
        mode='lines',
        name='Historical Sugar Price',
        line=dict(
            color='blue',  # Default color for the line
            width=2
        ),
        text=complete_data['Type'],  # Show data type on hover
        hovertemplate='%{x}<br>Sugar Price: Rs. %{y}<extra></extra>'
    ))

    # Highlight forecasted data by overlaying it
    fig.add_trace(go.Scatter(
        x=predictions['Date'],
        y=predictions['Sugar Price'],
        mode='lines',
        name='Forecasted Sugar Price',
        line=dict(
            color='#ff7f0e',
            width=2.5
        ),
        text=complete_data['Type'],  # Show data type on hover
        hovertemplate='%{x}<br>Sugar Price: Rs. %{y}<extra></extra>'
    ))

    # Add confidence intervals as a filled area
    fig.add_trace(go.Scatter(
        x=predictions['Date'].tolist() + predictions['Date'].tolist()[::-1],
        y=predictions['Conf Int (Upper)'].tolist() +
        predictions['Conf Int (Lower)'].tolist(),
        fill='toself',
        fillcolor='rgba(255, 182, 193, 0.3)',  # Light pink with transparency
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Interval'
        # hoverinfo="skip",
    ))

    # Update layout: X and Y axis labels, title, and ranges
    fig.update_layout(
        # title=f'Forecasted Indian Sugar Prices ({code_type})',
        xaxis_title='Date',
        yaxis_title='Sugar Price',
        xaxis=dict(
            # tickmode='linear',
            tickformat='%b-%Y',  # Format x-axis ticks to Month-Year
            tickangle=45,        # Rotate x-axis ticks
            showgrid=True,
            # ntick=12
        ),
        yaxis=dict(
            range=[
                # Set Y-axis lower limit with margin
                min(complete_data['Sugar Price']) * 0.95,
                # Set Y-axis upper limit with margin
                max(complete_data['Sugar Price']) * 1.05
            ],
            showgrid=True
        ),
        template='plotly_white',  # Clean background
        legend=dict(
            x=0.01, y=0.99,
            bordercolor="Black",
            borderwidth=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Table for prediction ({code_type})", divider=True)

    # dataframe for showcase

    df_show = complete_data[['Date', 'Sugar Price',
                             'Type', 'Conf Int (Lower)', 'Conf Int (Upper)']]
    df_show = df_show.sort_values('Date', ascending=False)
    df_show['Date'] = df_show['Date'].dt.strftime(r'%b-%Y')
    df_show.fillna('-', inplace=True)

    st.dataframe(df_show, width=1200, hide_index=True)
