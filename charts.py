from functions import portfolio_vs_benchmark
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



def NAV_chart(tx_df, custom_prices_df, date_range, bench):

    portfolio_vs_benchmark_df = portfolio_vs_benchmark(tx_df, custom_prices_df, date_range)
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.plot(portfolio_vs_benchmark_df.T['Date'], portfolio_vs_benchmark_df.T['portfolio'], label="portfolio")
    if bench != "":
        ax.plot(portfolio_vs_benchmark_df.T['Date'], portfolio_vs_benchmark_df.T[bench], label=bench)

    ax.set_title('Portfolio Performance vs ' + bench)
    if bench == "":
        ax.set_title('Portfolio Performance')
    ax.set_xlabel('Date')
    ax.set_ylabel('Unit Price')
    ax.legend()
    chart_file = 'static/NAV_chart.png'
    fig.savefig(chart_file)
    return chart_file

def current_vs_invested(df):
    fig, ax1 = plt.subplots(figsize=(15, 10))
    ax2 = ax1.twinx()

    ax1.set_title('Portfolio current value in SGD vs cumulative invested')
    ax1.plot(df['Cumul'], label='Cumul Invested')
    ax1.plot(df['Total Portfolio Value (SGD)'], label='Total Portfolio Value SGD')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Amount (SGD)')
    ax1.legend(loc='upper left')

    ax2.plot(df['Gains_Losses'], label='Gains/Losses', color='black')
    ax2.set_ylabel('Gains/Losses (SGD)')
    ax2.legend(loc='upper right')

    chart_file = 'static/current_vs_invested_chart.png'
    fig.savefig(chart_file)
    return chart_file

def scatter_orders_over_time(df, buys_df, sells_df, buy_bubble_sizes, sell_bubble_sizes):
    # create the scatter plot
    fig, ax = plt.subplots(figsize=(15, 10))

    # create the first y-axis for the scatter plots
    ax2 = ax.twinx()

    buy_scatter = ax.scatter(buys_df['Date'], buys_df['Amount'], s=buy_bubble_sizes, alpha=0.5, label="Buy")
    sell_scatter = ax.scatter(sells_df['Date'], sells_df['Amount'], s=sell_bubble_sizes, alpha=0.5, label='Sell')

    # get the handles and labels for the legend
    handles, labels = ax.get_legend_handles_labels()

    # create a dictionary to map the handles to the scatter objects
    scatter_map = {str(buy_scatter): buy_scatter, str(sell_scatter): sell_scatter}

    # create new scatter objects with the same size for the legend
    legend_buy_scatter = ax.scatter([], [], s=50, alpha=0.5, label="Buy", c=buy_scatter.get_facecolors()[0])
    legend_sell_scatter = ax.scatter([], [], s=50, alpha=0.5, label='Sell', c=sell_scatter.get_facecolors()[0])

    # update the handles to use the new scatter objects
    handles[handles.index(buy_scatter)] = legend_buy_scatter
    handles[handles.index(sell_scatter)] = legend_sell_scatter

    # add the updated handles and labels to the legend
    ax.legend(handles, labels, loc='upper left')

    # set the x-axis label and format the dates
    ax.set_xlabel('Date')
    fig.autofmt_xdate()

    # add labels to each bubble
    # for i, txt in enumerate(buys_df['Asset']):
    #     ax.annotate(txt, (buys_df['Date'].iloc[i], buys_df['Amount'].iloc[i]))

    # for i, txt in enumerate(sells_df['Asset']):
    #     ax.annotate(txt, (sells_df['Date'].iloc[i], sells_df['Amount'].iloc[i]))

    ax2.plot(df['Date'], df['Gains_Losses'], c="black", label="Gains & Losses")

    # set the y-axis label for the secondary y-axis
    ax2.set_ylabel('Gains & Losses')

    # get the handles and labels for the secondary y-axis
    handles2, labels2 = ax2.get_legend_handles_labels()

    # add the secondary y-axis handles and labels to the main legend
    handles += handles2
    labels += labels2
    ax.legend(handles, labels, loc='upper left')

    # save the figure
    chart_file = 'static/scatter_orders_over_time_chart.png'
    fig.savefig(chart_file)

    # return the path to the saved chart image file
    return chart_file


def pnl_by_stock(sorted_data):

    # create a bar graph with title, x-label, y-label, and values
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # set the color of the bars based on their values
    colors = ['green' if val >= 0 else 'red' for val in sorted_data.values()]
    
    # plot the bars with the corresponding colors
    ax.bar(sorted_data.keys(), sorted_data.values(), alpha=0.5, color=colors)
    
    ax.set_xticklabels(sorted_data.keys(), rotation=45)
    ax.set_title('P&L by asset (S$k)', fontsize=12)
    ax.set_xlabel('Assets', fontsize=8)
    ax.set_ylabel('Values (in thousands)', fontsize=10)
    
    # set font size of tick labels
    ax.tick_params(axis='both', which='major', labelsize=7)
    
    # add values to the top of each bar
    for i, v in enumerate(sorted_data.values()):
        ax.text(i, v, str(round(v/1000, 1)), ha='center', va='bottom')
    
    # format y-axis labels to display values in thousands
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:,.0f}'.format(y/1000) + 'K'))
    
    chart_file = 'static/pnl_chart.png'
    fig.savefig(chart_file)
    
    return chart_file


def portfolio_today_chart(portfolio_today_df):

    ### Add AA pie chart
    fig, ax = plt.subplots(figsize=(15, 10))
    plt.title('Asset Allocation')
    plt.pie(portfolio_today_df['val'], labels=portfolio_today_df['Asset_Name'], autopct='%1.1f%%')
    # Set the alpha value for the pie chart slices
    for wedge in ax.patches:
        wedge.set_alpha(0.5)
    chart_file = 'static/portfolio_today_chart.png'
    fig.savefig(chart_file)
    return chart_file