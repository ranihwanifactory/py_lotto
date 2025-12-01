import random
import streamlit as st

# ------------------------------
# 전략적 로또 번호 생성 로직
# ------------------------------
def is_valid(numbers, use_odd_even_rule, use_consecutive_rule):
    numbers = sorted(numbers)

    # 홀짝 3:3 규칙
    if use_odd_even_rule:
        odd = sum(1 for n in numbers if n % 2 == 1)
        even = 6 - odd
        if not (odd == 3 and even == 3):
            return False

    # 연속 번호 3개 이상 금지
    if use_consecutive_rule:
        consecutive = 1
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i - 1] + 1:
                consecutive += 1
                if consecutive >= 3:
                    return False
            else:
                consecutive = 1

    return True


def generate_lotto_numbers(
    count=5,
    use_odd_even_rule=True,
    use_consecutive_rule=True,
    fixed_numbers=None,
    excluded_numbers=None,
):
    """
    count                : 생성할 세트 개수
    use_odd_even_rule    : 홀짝 3:3 규칙 사용 여부
    use_consecutive_rule : 연속번호 3개 이상 금지 여부
    fixed_numbers        : 반드시 포함하고 싶은 번호 리스트
    excluded_numbers     : 절대 포함하고 싶지 않은 번호 리스트
    """

    fixed_numbers = fixed_numbers or []
    excluded_numbers = excluded_numbers or []

    results = []
    trials_limit = 10000  # 무한루프 방지

    while len(results) < count and trials_limit > 0:
        trials_limit -= 1

        # 사용할 수 있는 번호 pool 만들기
        available = [n for n in range(1, 46) if n not in excluded_numbers]

        # 고정 번호가 이미 너무 많으면 패스
        if len(fixed_numbers) > 6:
            break

        # 고정 번호 포함해서 부족한 개수만큼 랜덤 뽑기
        remaining_count = 6 - len(fixed_numbers)
        if remaining_count < 0:
            continue

        # available에서 fixed_numbers는 제외하고 추첨
        candidates_pool = [n for n in available if n not in fixed_numbers]

        if len(candidates_pool) < remaining_count:
            continue

        random_part = random.sample(candidates_pool, remaining_count)
        nums = sorted(fixed_numbers + random_part)

        if is_valid(nums, use_odd_even_rule, use_consecutive_rule):
            if nums not in results:
                results.append(nums)

    return results


# ------------------------------
# Streamlit 앱 UI
# ------------------------------
def main():
    st.set_page_config(
        page_title="로또 전략 번호 생성기",
        page_icon="🎰",
        layout="centered",
    )

    st.title("🎰 로또 전략 번호 생성기")
    st.markdown(
        """
        반복해서 찍던 번호 대신,  
        **간단한 규칙을 적용한 전략적인 번호 조합**을 만들어 드립니다.  
        아래 옵션을 선택하고 **[번호 생성하기]** 버튼을 눌러 보세요.
        """
    )

    st.divider()

    # 옵션 영역
    col1, col2 = st.columns(2)

    with col1:
        games = st.slider("생성할 번호 세트 개수", min_value=1, max_value=10, value=5)

    with col2:
        use_odd_even_rule = st.checkbox("홀짝 3:3 비율 유지", value=True)

    use_consecutive_rule = st.checkbox("연속 번호 3개 이상은 피하기", value=True)

    # 고정 번호 / 제외 번호 입력 (쉼표 구분)
    st.markdown("### 고급 옵션 (선택 사항)")

    fixed_input = st.text_input(
        "반드시 포함하고 싶은 번호 (예: 7, 13)",
        placeholder="비워두셔도 됩니다.",
    )
    excluded_input = st.text_input(
        "제외하고 싶은 번호 (예: 1, 2, 3)",
        placeholder="비워두셔도 됩니다.",
    )

    def parse_numbers(text):
        nums = []
        for part in text.replace(" ", "").split(","):
            if part.isdigit():
                n = int(part)
                if 1 <= n <= 45:
                    nums.append(n)
        return list(sorted(set(nums)))

    fixed_numbers = parse_numbers(fixed_input)
    excluded_numbers = parse_numbers(excluded_input)

    # 고정 번호와 제외 번호가 겹치는지 체크
    conflict = set(fixed_numbers) & set(excluded_numbers)
    if conflict:
        st.error(f"고정 번호와 제외 번호에 동시에 들어간 숫자: {sorted(conflict)}")

    st.divider()

    # 번호 생성 버튼
    if st.button("번호 생성하기 🎲", type="primary"):
        if len(fixed_numbers) > 6:
            st.error("고정 번호는 최대 6개까지만 가능합니다.")
        else:
            with st.spinner("번호를 생성하고 있습니다..."):
                results = generate_lotto_numbers(
                    count=games,
                    use_odd_even_rule=use_odd_even_rule,
                    use_consecutive_rule=use_consecutive_rule,
                    fixed_numbers=fixed_numbers,
                    excluded_numbers=excluded_numbers,
                )

            if not results:
                st.warning("설정한 조건이 너무 엄격해서 번호를 만들지 못했습니다. 조건을 완화해 주세요.")
            else:
                st.success(f"총 {len(results)}개의 번호 세트를 생성했습니다.")

                for idx, nums in enumerate(results, start=1):
                    with st.container():
                        st.markdown(f"#### 🎟️ 세트 {idx}")
                        # 번호를 예쁘게 라벨로
                        cols = st.columns(6)
                        for i, n in enumerate(nums):
                            cols[i].markdown(
                                f"""
                                <div style="text-align:center; border-radius: 999px; padding: 8px 0;
                                            border: 1px solid #ddd; font-size: 18px;">
                                    {n}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        st.markdown("---")

    st.markdown(
        """
        <small style='color: gray;'>
        ※ 이 앱은 당첨을 보장하지 않으며, 단순히 번호 선택을 돕기 위한 도구입니다.<br>
        최종 선택과 책임은 사용자에게 있습니다.
        </small>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
