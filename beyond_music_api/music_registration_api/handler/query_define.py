import os, sys
from pathlib import Path
sys.path.append(str(Path(os.path.abspath(__file__)).parent.parent) + '\handler')
from db_handler import Database
def get_transfer_daily_dict(date):
    """매일 전송하는 딕셔너리 쿼리문 리스트 추출"""
    takedown_track_query =f"""
    select
'Luminanat' AS 'rgstOrgnName',
t2.distTrackCode,
case
when (isnull(t2.TrackName_KR_Platform,'')) != '' then (isnull(t2.TrackName_KR_Platform,''))
when (isnull(t2.TrackName,'')) != '' then (isnull(t2.TrackName,''))
when (isnull(t2.TrackName_Eng,'')) != '' then (isnull(t2.TrackName_Eng,''))
when (isnull(t2.TrackName_CN,'')) != '' then (isnull(t2.TrackName_CN,''))
when (isnull(t2.TrackName_CN_2,'')) != '' then (isnull(t2.TrackName_CN_2,''))
when (isnull(t2.TrackName_JP,'')) != '' then (isnull(t2.TrackName_JP,''))
end as trackName,
1 AS 'nationcd',
case
when (isnull(d2.Album_KR_Platform,'')) != '' then (isnull(d2.Album_KR_Platform,''))
when (isnull(d2.Album,'')) != '' then (isnull(d2.Album,''))
when (isnull(d2.Album_Eng,'')) != '' then (isnull(d2.Album_Eng,''))
when (isnull(d2.Album_CN,'')) != '' then (isnull(d2.Album_CN,''))
when (isnull(d2.Album_CN_2,'')) != '' then (isnull(d2.Album_CN_2,''))
when (isnull(d2.Album_JP,'')) != '' then (isnull(d2.Album_JP,''))
end as albumName,
t2.Track_Lable,
t2.cd_num,
t2.track_seq,
convert(nvarchar(4), d2.ReleaseDate,120) AS 'albumIssuYear',
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 4
FOR XML PATH('')), 1, 1, '')),'없음' ) as Lyricist,
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 5
FOR XML PATH('')), 1, 1, '')),'없음' ) as comp,
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 6
FOR XML PATH('')), 1, 1, '')),'없음' ) as Arranger,
'없음' AS 'tran',
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'')
end
from ML_Track_Artist
where ml_track_seq = t2.seqno and (artistpart = 1  or artistpart = 2)
FOR XML PATH('')), 1, 1, '')),'없음' ) as artist,
'없음' AS 'perf',
'없음' AS 'prod',
'0' AS 'commMgntCd',
'0' AS 'liceMgntCd',
'0' AS 'perfMgntCd',
'0' AS 'prodMgntCd',
t2.UCICode,
'음반' as 'musicType'
from ml_track_type2 t2
left join ML_Detail_type2 d2
on d2.seqno = t2.ml_detail_seq
left join ML_List_Type2 l2
on t2.ml_detail_seq = l2.ml_detail_seq
left join Music_License_Dev.dbo.ML_Track_Type2_{str(date).replace("-", '_')}_00_00_00 dummy_track
on dummy_track.seqno = t2.seqno
left join Music_License_Dev.dbo.ML_Detail_Type2_{str(date).replace("-", '_')}_00_00_00 dummy_album
on dummy_album.seqno = d2.seqno
where t2.DistComid = 41 and l2.delete_state = 0 and (dummy_track.isService != t2.isService or (dummy_album.Excep_Policy_Code != d2.Excep_Policy_Code and d2.Excep_Policy_Code = 'CS10150'))
    """
    #takedown_track_query date format = 2022_09_23
    new_track_query = f"""
    select
'Luminanat' AS 'rgstOrgnName',
t2.distTrackCode,
case
when (isnull(t2.TrackName_KR_Platform,'')) != '' then (isnull(t2.TrackName_KR_Platform,''))
when (isnull(t2.TrackName,'')) != '' then (isnull(t2.TrackName,''))
when (isnull(t2.TrackName_Eng,'')) != '' then (isnull(t2.TrackName_Eng,''))
when (isnull(t2.TrackName_CN,'')) != '' then (isnull(t2.TrackName_CN,''))
when (isnull(t2.TrackName_CN_2,'')) != '' then (isnull(t2.TrackName_CN_2,''))
when (isnull(t2.TrackName_JP,'')) != '' then (isnull(t2.TrackName_JP,''))
end as trackName,
1 AS 'nationcd',
case
when (isnull(d2.Album_KR_Platform,'')) != '' then (isnull(d2.Album_KR_Platform,''))
when (isnull(d2.Album,'')) != '' then (isnull(d2.Album,''))
when (isnull(d2.Album_Eng,'')) != '' then (isnull(d2.Album_Eng,''))
when (isnull(d2.Album_CN,'')) != '' then (isnull(d2.Album_CN,''))
when (isnull(d2.Album_CN_2,'')) != '' then (isnull(d2.Album_CN_2,''))
when (isnull(d2.Album_JP,'')) != '' then (isnull(d2.Album_JP,''))
end as albumName,
t2.Track_Lable,
t2.cd_num,
t2.track_seq,
convert(nvarchar(4), d2.ReleaseDate,120) AS 'albumIssuYear',
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 4
FOR XML PATH('')), 1, 1, '')),'없음' ) as Lyricist,
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 5
FOR XML PATH('')), 1, 1, '')),'없음' ) as comp,
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 6
FOR XML PATH('')), 1, 1, '')),'없음' ) as Arranger,
'없음' AS 'tran',
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'')
end
from ML_Track_Artist
where ml_track_seq = t2.seqno and (artistpart = 1  or artistpart = 2)
FOR XML PATH('')), 1, 1, '')),'없음' ) as artist,
'없음' AS 'perf',
'없음' AS 'prod',
'0' AS 'commMgntCd',
'0' AS 'liceMgntCd',
'0' AS 'perfMgntCd',
'0' AS 'prodMgntCd',
t2.UCICode,
'음반' AS 'musicType'
from ml_track_type2 t2
left join ML_Detail_type2 d2
on d2.seqno = t2.ml_detail_seq
left join ML_List_Type2 l2
on t2.ml_detail_seq = l2.ml_detail_seq
where t2.DistComid = 41 AND d2.Reg_Date BETWEEN '{date} 00:00:00' AND '{date} 23:59:59' and d2.Excep_Policy_Code != 'CS10150' and t2.isService = 1
    """
    #new_track_query data format = 2022-09-23
    takedown_track_list = Database.execute_list(takedown_track_query, 'ml_live_select')
    new_track_list = Database.execute_list(new_track_query, 'ml_live_select')
    transfer_daily_list = takedown_track_list + new_track_list
    daily_dict_list = dict_format_list(transfer_daily_list)
    return daily_dict_list

def get_transfer_total_dict():
    """ 모든 루미넌트 전송 쿼리문 리스트 추출"""
    query = f"""select
'Luminanat' AS 'rgstOrgnName',
t2.distTrackCode,
case
when (isnull(t2.TrackName_KR_Platform,'')) != '' then (isnull(t2.TrackName_KR_Platform,''))
when (isnull(t2.TrackName,'')) != '' then (isnull(t2.TrackName,''))
when (isnull(t2.TrackName_Eng,'')) != '' then (isnull(t2.TrackName_Eng,''))
when (isnull(t2.TrackName_CN,'')) != '' then (isnull(t2.TrackName_CN,''))
when (isnull(t2.TrackName_CN_2,'')) != '' then (isnull(t2.TrackName_CN_2,''))
when (isnull(t2.TrackName_JP,'')) != '' then (isnull(t2.TrackName_JP,''))
end as trackName,
1 AS 'nationcd',
case
when (isnull(d2.Album_KR_Platform,'')) != '' then (isnull(d2.Album_KR_Platform,''))
when (isnull(d2.Album,'')) != '' then (isnull(d2.Album,''))
when (isnull(d2.Album_Eng,'')) != '' then (isnull(d2.Album_Eng,''))
when (isnull(d2.Album_CN,'')) != '' then (isnull(d2.Album_CN,''))
when (isnull(d2.Album_CN_2,'')) != '' then (isnull(d2.Album_CN_2,''))
when (isnull(d2.Album_JP,'')) != '' then (isnull(d2.Album_JP,''))
end as albumName,
Track_Lable,
t2.cd_num,
t2.track_seq,
convert(nvarchar(4), d2.ReleaseDate,120) AS 'albumIssuYear',
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 4
FOR XML PATH('')), 1, 1, '')),'없음' ) as Lyricist,
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 5
FOR XML PATH('')), 1, 1, '')),'없음' ) as comp,
isnull((SELECT
    STUFF((
selecT ','+  case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'') end from ML_Track_Artist
where ml_track_seq = t2.seqno and artistpart = 6
FOR XML PATH('')), 1, 1, '')),'없음' ) as Arranger,
'없음' AS 'tran',
isnull((SELECT
    STUFF((
selecT ','+ case
when isnull(artistname_kr_platform,'') != '' then isnull(artistname_kr_platform,'')
when isnull(artistname_kr,'') != '' then isnull(artistname_kr,'')
when isnull(artistname_eng,'') != '' then isnull(artistname_eng,'')
when isnull(artistname_jp,'') != '' then isnull(artistname_jp,'')
when isnull(artistname_cn_simplified,'') != '' then isnull(artistname_cn_simplified,'')
when isnull(artistname_cn_traditional,'') != '' then isnull(artistname_cn_traditional,'')
end
from ML_Track_Artist
where ml_track_seq = t2.seqno and (artistpart = 1  or artistpart = 2)
FOR XML PATH('')), 1, 1, '')),'없음' ) as artist,
'없음' AS 'perf',
'없음' AS 'prod',
'0' AS 'commMgntCd',
'0' AS 'liceMgntCd',
'0' AS 'perfMgntCd',
'0' AS 'prodMgntCd',
t2.UCICode,
'음반' AS 'musicType'
from ml_track_type2 t2
left join ML_Detail_type2 d2
on d2.seqno = t2.ml_detail_seq
left join ML_List_Type2 l2
on t2.ml_detail_seq = l2.ml_detail_seq
where t2.DistComid = 41 and l2.delete_state = 0 and d2.Excep_Policy_Code != 'CS10150' and t2.isService = 1"""
    transfer_total_dict = Database.execute_list(query, 'ml_live_select')
    total_dict_list = dict_format_list(transfer_total_dict)
    return total_dict_list

def dict_format_list(transfer_list):
    """딕셔너리 전송 포맷"""
    total_list = []
    total_dict = {}
    for dict in transfer_list:
        list = {}
        list["rgstOrgnName"] = dict['rgstOrgnName']
        list["commWorksId"] = dict['distTrackCode']
        list["worksTitle"] = dict['trackName']
        list["nationcd"] = dict['nationcd']
        list["albumTitle"] = dict['albumName']
        list["albumLable"] = dict['Track_Lable']
        list["diskSide"] = dict['cd_num']
        list["trackNo"] = dict['track_seq']
        list["albumIssuYear"] = dict['albumIssuYear']
        list["lyrc"] = dict['Lyricist']
        list["comp"] = dict['comp']
        list["arra"] = dict['Arranger']
        list["tran"] = dict['tran']
        list["sing"] = dict['artist']
        list["perf"] = dict['perf']
        list["prod"] = dict['prod']
        list["commMgntCd"] = dict['commMgntCd']
        list["liceMgntCd"] = dict['liceMgntCd']
        list["perfMgntCd"] = dict['perfMgntCd']
        list["prodMgntCd"] = dict['prodMgntCd']
        list["uci"] = dict['UCICode']
        list["musicType"] = dict['musicType']
        total_dict["totalCnt"] = len(transfer_list)
        total_dict["list"] = list
        total_list.append(total_dict)
    return total_list