while True:
    team_name = input('팀의 이름을 입력하세요 >> ')

    while True:
        try:
            total_game = int(input('총 경기의 횟수를 입력하세요 >> '))

            # 득점과 실점을 저장할 리스트
            list_w = list()
            list_l = list()

            # 경기 결과 입력
            for i in range(total_game):
                w = int(input(f'{i + 1} 번째 경기의 득점을 입력하세요 >> '))
                l = int(input(f'{i + 1} 번째 경기의 실점을 입력하세요 >> '))
                print("+" * 20)

                list_w.append(w)
                list_l.append(l)

            # 총 득점과 총 실점 계산
            checksum_w = sum(list_w)
            checksum_l = sum(list_l)

            print(f'{team_name}의 총 득점은 {checksum_w}점, 총 실점은 {checksum_l}점 입니다.')

            checksum_code = input('위 내용이 맞다면 0, 아니면 1을 입력하세요 >> ')

            if checksum_code == '0':
                # 피타고리안 승률 계산
                pythagorean_exp = (checksum_w ** 2) / ((checksum_w ** 2) + (checksum_l ** 2))
                print(f'{team_name}의 피타고리안 승률은 {pythagorean_exp:.2f} 입니다.')
                break
            else:
                print('입력이 잘못되었습니다. 다시 입력해주세요.')
        except ValueError:
            print('잘못된 입력입니다. 숫자를 입력해주세요.')

    # 모든 입력이 끝난 후, 전체 프로그램을 종료할지 여부를 묻습니다.
    exit_code = input('프로그램을 종료하려면 0을 입력하세요. 계속하려면 1을 입력하세요 >> ')
    if exit_code == '0':
        break
