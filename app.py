import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# 파일 경로 및 데이터 처리를 위한 상수
F_URL = './data/202205.csv'  # CSV 데이터 파일 경로
YEAR, MONTH = F_URL[7:11], F_URL[11:13]  # 파일 이름에서 연도와 월 추출


# DataFrame 정리 함수
def clean_df(df):
    """
    DataFrame을 정리하여 열 이름을 조직하고 지역 이름을 형식화합니다.
    """
    df = replace_col_name(df)
    df['행정구역'] = df['행정구역'].apply(format_district_name)
    df = convert_columns_to_numeric(df, ['행정구역'])
    return df

# 데이터를 불러오고 정리하는 함수
def load_and_clean_data(file_path):
    """
    주어진 CSV 파일 경로에서 데이터를 불러오고 정리합니다.
    """
    df = pd.read_csv(file_path, encoding='cp949', thousands=',')
    df = clean_df(df)
    return df

def replace_col_name(df):
    """
    불필요한 접두사를 제거하여 열 헤더를 조직합니다.
    """
    new_col_name = [i.split('월_')[1] if '월_' in i else i for i in df.columns]
    df.columns = new_col_name
    return df

def format_district_name(col):
    """
    괄호를 제거하고 필요한 경우 'all'을 추가하여 지역 이름을 형식화합니다.
    """
    col = " ".join(col.split('(')[:-1]).strip()
    parts = col.split(" ")

    # parts 리스트의 각 요소에 안전하게 접근하기 위한 검사
    if len(parts) >= 3:
        if parts[1].endswith('시') and parts[2].endswith('구'):
            col += " 전체"
    return col


def convert_columns_to_numeric(df, exclude_cols):
    """
    exclude_cols에 없는 모든 열을 숫자 형식으로 변환합니다.
    """
    cols_to_convert = df.columns.difference(exclude_cols).tolist()
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric)
    return df

# 데이터 불러오기 및 정리
df = load_and_clean_data(F_URL)

# Streamlit 앱 구성
def main():
    st.title("인구 통계 데이터 애플리케이션")

    # 연도와 월 표시
    st.write(f"데이터 연도: {YEAR}, 월: {MONTH}")

    # 도시 이름 입력
    city = st.text_input("도시 이름을 입력하세요:")

    if city:
        city, df_city = input_city(city, df)
        if len(df_city) > 1:
            st.write("여러 지역이 검색되었습니다. 하나를 선택해주세요.")
            selected = st.selectbox("지역 선택:", df_city['행정구역'])
            city, df_city = input_city(selected, df)
            show_data(df_city)
        else:
            show_data(df_city)

def input_city(city, df):
    """
    입력된 도시 이름에 따라 DataFrame을 필터링합니다.
    """
    city_df = df[df['행정구역'].str.contains(city)]
    if len(city_df) > 1:
        return city, city_df
    return city, city_df.iloc[0]

def show_data(df_city):
    """
    특정 도시의 인구 통계 데이터를 표시합니다.
    """
    combined_data, sum_man, sum_woman, sum_all = make_data(df_city)
    st.write(f"총 인구: {sum_all}, 남성: {sum_man}, 여성: {sum_woman}")

    # 남성과 여성 데이터를 가로축에 따라 그래프로 시각화
    fig, ax = plt.subplots()
    ax.barh(combined_data['Age'], combined_data['Male'], color='blue', label='Male')
    ax.barh(combined_data['Age'], -combined_data['Female'], color='pink', label='Female')
    ax.set_xlabel('Population')
    ax.set_ylabel('Age')
    ax.legend()
    ax.set_title('Population by Age and Gender')

    # Streamlit에 그래프 표시
    st.pyplot(fig)



def make_data(df_city):
    """
    특정 도시에 대한 남성 및 여성 인구 통계 데이터를 처리하고 결합합니다.
    """
    label = list(range(101))  # 나이 범위 (0-100)
    data_man = df_city.iloc[:, 3:104].values.tolist()[0]
    data_woman = df_city.iloc[:, 106:207].values.tolist()[0]

    # 남성 및 여성 데이터를 DataFrame으로 결합
    combined_data = pd.DataFrame({
        'Age': label,
        'Male': data_man,
        'Female': data_woman
    })

    sum_man, sum_woman = df_city.iloc[0, 1], df_city.iloc[0, 104]
    sum_all = sum_man + sum_woman
    return combined_data, sum_man, sum_woman, sum_all


if __name__ == "__main__":
    main()
