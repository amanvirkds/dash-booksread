import pandas as pd
import re
import math
import datetime
from dash import html

def ret_dict_awards(row):
    id=row['book_id']
    book_id=[]
    award_str=[]
    awards=[]
    award_year=[]
    if isinstance(row.awards,str):
        award_list=row.awards.split(",")
        for award in award_list:
            book_id.append(int(id))
            award_str.append(award)
            awardyr=re.findall("[0-9][0-9][0-9][0-9]", award)
            if len(awardyr)>0:
                awards.append(award.replace("("+awardyr[0]+")","").strip())
                award_year.append(int(awardyr[0]))
            else:
                awards.append(award)
                award_year.append("")
            
    return {'book_id':book_id,'award_str':award_str,'awards':awards,'award_year':award_year}
        
def ret_df_awards(df):
    dfs=[]
    for idx in range(df.shape[0]):
        dfs.append(pd.DataFrame(df.awards_dict[idx]))
    df_awards=pd.concat(dfs)
    df_awards=df_awards.reset_index()
    df_awards.book_id=df_awards.book_id.apply(lambda x: int(x))


    df_book_awards=df_awards.join(df[['book_id','title','series','author']].set_index(
        'book_id'),how="inner",on=['book_id'])
    df_book_awards=df_book_awards.reset_index()
    df_book_awards=df_book_awards[['book_id','awards','award_year']]
    df_book_awards['award_year']=df_book_awards['award_year'].apply(lambda x: 'NA' if x=='' else x)
    cols=df_book_awards.columns
    df_book_awards_cp=df_book_awards.copy()

    df_book_awards_cp['flag']=df_book_awards.award_year.apply(
        lambda x: True if (0 if x=='NA' else int(x))>=1980 else False)
    df_book_awards=df_book_awards_cp.loc[df_book_awards_cp.flag==True,cols]
    return df_book_awards


def ret_date(year,days):
    dt=(datetime.date(year,1,1)+datetime.timedelta(days=-1))+datetime.timedelta(days=days)
    return dt.strftime("%Y-%m-%d")

def ret_awddates(award_year,awards):
    if award_year=='NA':
        award_year=2020

    awdcount=awards
    step=math.floor(365/awdcount)
    startdt=None
    enddt=None
    dtlist=[]
    for i in range(1,365,step):
        if i==1:
            startdt=i
            continue
        else:
            enddt=i-1
            dtlist.append((startdt,enddt))
            startdt=i
    if awdcount==1:
        dtlist.append((1,365))
    elif len(dtlist)<awdcount:
        dtlist.append((dtlist[0][1]+1,365))
    dtlist2=[(ret_date(award_year,dt[0]),ret_date(award_year,dt[1])) for dt in dtlist]
    return(dtlist2)
def retawardDt(df_awardsByYear):
    df_awardsCntYear=df_awardsByYear.groupby(['book_id','title','award_year']).agg(awdcount=(
    'book_id','count')).reset_index().sort_values(by=['awdcount'],ascending=False)
    df_awardsCntYear['awd_dates']=df_awardsCntYear.apply(
        lambda row: ret_awddates(row['award_year'],row['awdcount']),axis=1)
    df_awardsByYear['StDate']='2008-01-01'
    df_awardsByYear['EdDate']='2008-12-31'

    for idx in range(df_awardsCntYear.shape[0]):
        book_id=df_awardsCntYear.loc[idx,'book_id']
        award_year=df_awardsCntYear.loc[idx,'award_year']
        awd_dates=df_awardsCntYear.loc[idx,'awd_dates']
        i=0
        for awdidx in df_awardsByYear.loc[(df_awardsByYear.book_id==book_id) &
                                          (df_awardsByYear.award_year==award_year),:].index:
            df_awardsByYear.loc[awdidx,'StDate']=awd_dates[i][0]
            df_awardsByYear.loc[awdidx,'EdDate']=awd_dates[i][1]
    return df_awardsByYear
    
def process_data(DATA_FILE):
    df=pd.read_csv(DATA_FILE)
    print("dataset contains %d rows nad %d columns" % (df.shape))
    df=df.rename(columns={'Unnamed: 0':'book_id'})
    df['avg_rating']=df.avg_rating.apply(lambda x: round(float(x.replace("['","").replace("']","")),2))
    df['no_ratings']=df.no_ratings.apply(lambda x: int(float(x.replace(",",""))))
    df=df[['book_id', 'title', 'language', 'series', 'author', 'pages',
        'avg_rating', 'no_ratings', 'description','awards']]
    df['awards_dict']=df.apply(lambda row: ret_dict_awards(row),axis=1)
    df['avg_rating']=df.avg_rating.apply(lambda x: round(x,1))
    df_book_awards=ret_df_awards(df)
    df=df[['book_id', 'title', 'language', 'series', 'author', 'pages',
        'avg_rating', 'no_ratings', 'description']]
    df_awardsByYear=df.join(df_book_awards.set_index(['book_id']),how="inner",on=['book_id']).groupby(
        ['award_year']).agg(AwardCount=('book_id','count')).reset_index()


    df_awardsByYear=df.join(df_book_awards.set_index(['book_id']),how="inner",on=['book_id'])
    df_awardsByYear=df_awardsByYear.reset_index()
    df_awardsByYear=retawardDt(df_awardsByYear)
    return(df,df_awardsByYear)

def ret_string(x_string):
    wds=x_string.split(" ")
    n_wds=5
    if len(wds)>n_wds:
        ret_str=" ".join(wds[:n_wds]+['<br>']+wds[n_wds:])
    else:
        ret_str=" ".join(wds)
    return ret_str

def chart_data(groupby_col,sort_column,df,df_awardsByYear,n):
    df_summary=df.groupby(groupby_col).agg(
        book_count=('book_id','count'),
        avg_rating=('avg_rating','mean'),
        no_ratings=('no_ratings','sum')).reset_index()
    df_summary['avg_rating']=df_summary.avg_rating.apply(lambda x: round(x,1))
    df_awards_count=df_awardsByYear.groupby(groupby_col).agg(
        award_count=('book_id','count')).reset_index()
    df_summary=df_summary.join(df_awards_count.set_index(groupby_col),how="inner",on=groupby_col)
    df_summary=df_summary.sort_values(by=sort_column,ascending=False).head(n)

    return df_summary

def return_books(retText):
    retText=str(retText)
    htmlString=""
    param_list=[]
    is_title=True if retText.find("Title:")>0 else False
    if is_title:
        newText=retText
        newText=newText.split("<br>")
        series=newText[2].replace("Series: ","")
        title=newText[3].replace("Title: ","")
        author=newText[4].replace("Author: ","")
        htmlString=html.H5(title)

        param_list=[title,series,author]
    
    return htmlString, param_list