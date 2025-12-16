def format_response(ticker, amount, best_model_name, best_model_info, recommendations):
    response = f"<b>Results of the analysis for {ticker}</b>\n\n"

    response += f"<b>Current price:</b> ${recommendations['current_price']:.2f}\n"
    response += f"<b>Best model:</b> {best_model_name}\n"
    response += f"<b>RMSE:</b> {best_model_info['rmse']:.4f}\n\n"

    response += f"<b>30-day forecast</b>\n"
    response += f"- Expected change percentage: {recommendations['price_change_percent']:+.2f}%\n"
    response += f"- Minimal price: ${recommendations['min_forecast_price']:.2f} (day {recommendations['buy_day']})\n"
    response += f"• Max price: ${recommendations['max_forecast_price']:.2f} (day {recommendations['sell_day']})\n\n"

    response += f"<b>Trading recommendations:</b>\n"
    if recommendations['buy_day'] and recommendations['sell_day']:
        response += f"- Purchase, recommended day {recommendations['buy_day']}\n"
        response += f"- Sale, recommended day {recommendations['sell_day']}\n"
    else:
        response += "- No sale or purchase recommended\n"

    response += f"\n<b>Potential profit:</b>\n"
    response += f"- Investing ${amount:,.2f}\n"
    response += f"- Profit: ${recommendations['potential_profit']:,.2f}\n"
    response += f"- ROI: {recommendations['roi']:+.2f}%\n\n"

    response += "<i>Attention: This is a forecast based on historical data and does not constitute financial advice.</i>"

    return response
