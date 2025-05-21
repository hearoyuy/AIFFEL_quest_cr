import 'package:flutter/material.dart';

class RelationSection extends StatelessWidget {
  final bool isEmployeeChecked;
  final bool isBusinessCounterpartyChecked;
  final void Function({bool? isEmployee, bool? isBusinessCounterparty}) onCheckboxChanged; // 체크박스 변경 콜백
  final VoidCallback onNextStepPressed; // 다음 단계 버튼 콜백

  const RelationSection({
    Key? key,
    required this.isEmployeeChecked,
    required this.isBusinessCounterpartyChecked,
    required this.onCheckboxChanged,
    required this.onNextStepPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Center(
          child: Text( // 설명 텍스트
            'Please let us know your relation with the entity.',
            style: TextStyle(fontSize: 14),
          ),
        ),
        const SizedBox(height: 8),
        Row( // 체크박스들을 가로로 배열
          children: [
            Row( // Employee 체크박스 그룹
              mainAxisSize: MainAxisSize.min,
              children: [
                Checkbox( // Employee 체크박스
                  value: isEmployeeChecked, // 현재 상태 연결
                  onChanged: (bool? newValue) {
                    onCheckboxChanged(isEmployee: newValue); // 부모 위젯에 상태 변경 알림
                  },
                ),
                const Text('Employee'), // 라벨
              ],
            ),
            const SizedBox(width: 20), // 간격
            Row( // Business Counterparty 체크박스 그룹
              mainAxisSize: MainAxisSize.min,
              children: [
                Checkbox( // Business Counterparty 체크박스
                  value: isBusinessCounterpartyChecked, // 현재 상태 연결
                  onChanged: (bool? newValue) {
                    onCheckboxChanged(isBusinessCounterparty: newValue); // 부모 위젯에 상태 변경 알림
                  },
                ),
                  const Text('Business Counterparty'), // 라벨
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        Align( // 버튼 정렬
          alignment: Alignment.centerRight,
          child: TextButton( // 다음 단계 버튼
            onPressed: onNextStepPressed, // 부모 위젯에 버튼 클릭 알림
            child: const Center(
              child: Text(
                'To Next Step >>',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ),
      ],
    );
  }
}