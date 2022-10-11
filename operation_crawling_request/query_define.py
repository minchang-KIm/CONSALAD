import query_define
from db_handler import Database

def artist_create_query(kor, eng, artist_id, memo):
    query = f'''
        Insert into ML_Artist_Info 
        (Artist_Name,Artist_Name_ENG,Apple_ID,State,Is_Create_Apple_Id,Etc) 
        VALUES ('{kor}','{eng}','{artist_id}',1,1,'{memo}')
    '''

    return query

# db 에 있을시 id 값 반환 업을시 None 리턴
def find_apple_id_from_consalad(kor_name, eng_name):
    # 이름에 D'CID 같은 케이스
    kor_name_ = str(kor_name).replace("'", "_").replace(" ", "").replace("`", "_")
    kor_name_wildcard = ("%".join(kor_name_))
    eng_name_ = str(eng_name).replace("'", "_").replace(" ", "").replace("`", "_")
    eng_name_wildcard = ("%".join(eng_name_))       #콘샐러드 디비 검색용으로 사용
    if eng_name == '':          #콘샐러드디비 null과 비교할때 사용
        eng_name = None
    if eng_name_wildcard == '':     #영문이 비어있을 때
        print("쿼리 1")
        query = f"""
                select top 1 Apple_ID, Artist_Name, Artist_Name_ENG  
                from ML_Artist_Info
                where ISNULL(Artist_Name,'') LIKE  N'{kor_name_wildcard}' and State = 1
                order by len(ISNULL(Artist_Name,'')) asc, len(ISNULL(Artist_Name_ENG,'')) asc, Seqno desc
            """
    else:                       #영문이 존재할 때
        print("쿼리2")
        query = f"""
                select top 1 Apple_ID, Artist_Name, Artist_Name_ENG  
                from ML_Artist_Info
                where ISNULL(Artist_Name,'') LIKE  N'{kor_name_wildcard}' and ISNULL(Artist_Name_ENG,'') LIKE  N'{eng_name_wildcard}' and State = 1
                order by len(ISNULL(Artist_Name,'')) asc, len(ISNULL(Artist_Name_ENG,'')) asc, Seqno desc
            """

    artist_info = Database.execute_list(query, 'ml_live_select')
    try:
        db_kor_name = artist_info[0]["Artist_Name"].replace(" ", "").replace("'", "_").replace("`", "_")
        db_eng_name = artist_info[0]["Artist_Name_ENG"]
        if db_kor_name == kor_name_ and (db_eng_name == eng_name or db_eng_name.replace(" ", "") == eng_name):
            return artist_info[0]["Apple_ID"]   #엑셀과 동일할 때
        elif db_kor_name == kor_name_ and db_eng_name != None and eng_name == None:
            return artist_info[0]["Apple_ID"]   #디비에 한문 영문 둘다 존재하고 한문이 같고 엑셀 영문이 존재하지 않을 때
        else:
            print("DB에서 못찾음")
            return None
    except Exception as e:
        print("DB에서 못찾음",e)
        return None

def get_dist_name_from_isrc(isrc):
    # 쿼리 코드 실행후
    query = f"""
        select Company_Name from ML_Distribution_Company where Seqno in(select DistComid from ML_Detail_type2 where seqno in(select ml_detail_seq from ML_Track_Type2 where ISRC = '{isrc}'))
        """
    ret_dict_list = Database.execute_list(query, 'ml_live_select')
    if len(ret_dict_list) == 0:
        return "NULL"
    else:
        return ret_dict_list[0]["Company_Name"]

if __name__ == "__main__":
    print(find_apple_id_from_consalad('영 팝스 오케스트라', 'Young Pop`s Orchestra'))
