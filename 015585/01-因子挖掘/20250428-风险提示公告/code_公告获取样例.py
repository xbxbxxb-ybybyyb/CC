from xquant.textdata import NewsData

nd = NewsData()
news_info = nd.getAnnouncement(['600519.SH'], '20200101', '20250331')
newID_list = news_info['ORIGINALCODE'].map(int).tolist()
def get_news_content(newID_list):
    nd = NewsData()
    news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]
    length = news_bodies_df[news_bodies_df['CONTENT'].apply(len) > 50]
    print(length)
    return length
from joblib import Parallel, delayed
factor_df_list = Parallel(n_jobs=28)(delayed(get_news_content)(newID_list) for i in range(1,60))

