import math
import numpy as np

### Plotly libraries
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from dash import dcc, html

from processing import chart_data, ret_string

BAR_COLOR="#add4ed"

def ret_viz(groupby_col,sort_column,df,df_awardsByYear,viz_template,n=100):
    df_summary=chart_data(groupby_col,sort_column,df,df_awardsByYear,n)
    traces_awards=[]
    df_awardsByYear=df_awardsByYear.join(df_summary[[groupby_col]].set_index(
        [groupby_col]),how="inner",on=[groupby_col])
    


    df_awardsByYear['hover_data']= df_awardsByYear.apply(
        lambda row: 
            str(row['award_year']) +"<br>" + \
            "Award: " + str(row['awards']) +"<br>" + \
            "Series: " + str(row['series']) +"<br>" + \
            "Title: " + str(row['title']) +"<br>" + \
            "Author: " + str(row['author'])
            
            ,axis=1)

    df_awardsByYear[groupby_col]=df_awardsByYear[groupby_col].apply(
         lambda x: ret_string(x))
    df_summary[groupby_col]=df_summary[groupby_col].apply(
         lambda x: ret_string(x))
    for award in df_awardsByYear.awards.unique():
        df_awardsByYear_sub=df_awardsByYear.loc[df_awardsByYear.awards==award,:]
        awards=df_awardsByYear_sub.awards
        award_year=df_awardsByYear_sub.award_year
        
        traces_awards.append(go.Scatter(y=df_awardsByYear_sub[groupby_col],
                                        x=df_awardsByYear_sub.StDate,
                                        mode="markers",
                                        hoverinfo="text",
                                        text=df_awardsByYear_sub['hover_data'],
                                        marker=dict(size=12)))

    trace_books=go.Bar(
        y=df_summary[groupby_col],
        x=df_summary.book_count,
        orientation="h",
        text=df_summary.book_count,
        textposition='auto',
        marker_color=BAR_COLOR,
        hoverinfo="text",
        width=.6)
    trace_avgrating=go.Bar(
        y=df_summary[groupby_col],
        x=df_summary.avg_rating,
        orientation="h",
        text=df_summary.avg_rating,
        textposition='auto',
        marker_color=BAR_COLOR,
        hoverinfo="text",
        width=.6)
    trace_norating=go.Bar(
        y=df_summary[groupby_col],
        x=df_summary.no_ratings,
        orientation="h",
        text=df_summary.no_ratings,
        textposition='auto',
        hoverinfo="text",
        marker_color=BAR_COLOR,
        width=.6)
    trace_awdcount=go.Bar(
        y=df_summary[groupby_col],
        x=df_summary.award_count,
        orientation="h",
        text=df_summary.award_count,
        textposition='auto',
        hoverinfo="text",
        marker_color=BAR_COLOR,
        width=.6)


    fig = make_subplots(
        rows=1, cols=8,
        shared_yaxes=True,
        horizontal_spacing=.03,
        specs=[[{"type": "scatter",'colspan':4},
                {"type": "scatter",'colspan':4},
                {"type": "scatter",'colspan':4},
                {"type": "scatter",'colspan':4},
                {"type": "bar",'colspan':1},
                {"type": "bar",'colspan':1},
                {"type": "bar",'colspan':1},
                {"type": "bar",'colspan':1}
               ]]
    )

    order_array=df_summary.sort_values(by=sort_column,ascending=True)[groupby_col].tolist()


    n_height=len(order_array)
    n_height=n_height*(50-int(n_height/math.sqrt(n_height)))

    for trace in traces_awards:
        fig.add_trace(trace, row=1, col=1)

    fig.add_trace(trace_books,row=1, col=5)
    fig.add_trace(trace_avgrating,row=1, col=6)
    fig.add_trace(trace_norating,row=1, col=7)
    fig.add_trace(trace_awdcount,row=1, col=8)

    fig.update_yaxes(showgrid=True,showticklabels=True, gridcolor='#0a454a',col=1)
    fig.update_yaxes(showticklabels=False,zeroline=False,showgrid=False,col=5)
    fig.update_yaxes(showticklabels=False,zeroline=False,showgrid=False,col=6)
    fig.update_yaxes(showticklabels=False,zeroline=False,showgrid=False,col=7)
    fig.update_yaxes(showticklabels=False,zeroline=False,showgrid=False,col=8)
    fig.update_xaxes(showgrid=False,showticklabels=False, col=1)
    fig.update_xaxes(showticklabels=False,zeroline=False,showgrid=False,col=5)
    fig.update_xaxes(showticklabels=False,zeroline=False,showgrid=False,col=6)
    fig.update_xaxes(showticklabels=False,zeroline=False,showgrid=False,col=7)
    fig.update_xaxes(showticklabels=False,zeroline=False,showgrid=False,col=8)

    #fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        showlegend=False,
        template=viz_template,
        yaxis={'categoryorder':'array', 'categoryarray':order_array},
        height=n_height,
        margin=dict(l=300, r=100, t=2, b=2)
        )
    return fig


def viz_template():
    viz_template = dict(
        layout=go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_font=dict(
                family="ariel", 
                size=24,
                color="#add4ed",
            ),
            font=dict(
                family="ariel",
                color="#add4ed",
                size=12
            ),
            yaxis=dict(automargin=False,autorange=True),
            xaxis=dict(
                automargin=True,
                autorange=True,
                showgrid=False
            )
    ))
    return viz_template


def ret_timeline(df,df_awardsByYear,viz_template,param_list=[]):

    ## data series

    traces_title=[]
    traces_series=[]
    traces_author=[]
    print(param_list)


    if len(param_list)>0:
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0,
            specs=[[{"type": "scatter"}],
                [{"type": "scatter"}],
                [{"type": "scatter"}]]
        )
        df_awards=[]
        
        
        idx=-1
        if param_list[0]!="nan":
            idx+=1
            ## plot traces for title
            df_awards.append(df_awardsByYear.loc[df_awardsByYear.title==param_list[0],])
            df_awards[idx]['title']=df_awards[idx]['title'].apply(lambda x: ret_string(x))
            df_awards[idx]['hover_data']= df_awards[idx].apply(
                lambda row: 
                    str(row['award_year']) +"<br>" + \
                    "Award: " + str(row['awards']),axis=1)
            for award in df_awards[idx].awards.unique():
                df_sub=df_awards[idx].loc[df_awards[idx].awards==award,:]    
                traces_title.append(
                    go.Scatter(y=df_sub['title'],
                    x=df_sub.StDate,
                    mode="markers",
                    hoverinfo="text",
                    text=df_sub['hover_data'],
                    marker=dict(size=12)))
            for trace in traces_title:
                fig.add_trace(trace, row=1, col=1)
        
        if param_list[1]!="nan":
            idx+=1
            ## plot traces for series
            df_awards.append(df_awardsByYear.loc[df_awardsByYear.series==param_list[1],])
            df_awards[idx]['series']=df_awards[idx]['series'].apply(lambda x: ret_string(x))
            df_awards[idx]['hover_data']= df_awards[1].apply(
                lambda row: 
                    str(row['award_year']) +"<br>" + \
                    "Award: " + str(row['awards']),axis=1)
            for award in df_awards[idx].awards.unique():
                df_sub=df_awards[idx].loc[df_awards[idx].awards==award,:]    
                traces_series.append(
                    go.Scatter(y=df_sub['series'],
                    x=df_sub.StDate,
                    mode="markers",
                    hoverinfo="text",
                    text=df_sub['hover_data'],
                    marker=dict(size=12)))
            for trace in traces_series:
                fig.add_trace(trace, row=2, col=1)

        if param_list[2]!="nan":
            idx+=1
            ## plot traces for author
            df_awards.append(df_awardsByYear.loc[df_awardsByYear.author==param_list[2],])
            df_awards[idx]['author']=df_awards[idx]['author'].apply(lambda x: ret_string(x))
            df_awards[idx]['hover_data']= df_awards[idx].apply(
                lambda row: 
                    str(row['award_year']) +"<br>" + \
                    "Award: " + str(row['awards']),axis=1)
            for award in df_awards[idx].awards.unique():
                df_sub=df_awards[idx].loc[df_awards[idx].awards==award,:]    
                traces_author.append(
                    go.Scatter(y=df_sub['author'],
                    x=df_sub.StDate,
                    mode="markers",
                    hoverinfo="text",
                    text=df_sub['hover_data'],
                    marker=dict(size=12)))
            for trace in traces_author:
                fig.add_trace(trace, row=3, col=1)

        fig.update_layout(
            showlegend=False,
            template=viz_template,
            height=190,
            margin={'t':20,'b':2,'l':190,'r':50}
        )
        return dcc.Graph(figure={'data':fig['data'],'layout':fig['layout']})
    else:
        return dcc.Graph(figure={'data':[],'layout':[]})