import 'package:flutter/material.dart';

class BusinessEntitySection extends StatelessWidget {
  const BusinessEntitySection({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text( // 설명 텍스트
          'Please select the business entity to whom your document to be submitted.',
          style: TextStyle(fontSize: 14),
        ),
        const SizedBox(height: 8),
        TextField( // 사업체 이름 입력 필드
          decoration: InputDecoration(
            hintText: 'Business Entity Name',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(5.0),
              borderSide: BorderSide.none,
            ),
            filled: true,
            fillColor: Colors.grey[200],
            contentPadding:
            const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0),
            suffixIcon: const Icon(Icons.search), // 검색 아이콘
          ),
        ),
        const SizedBox(height: 8),
        TextField( // 사업체 번호 입력 필드
          decoration: InputDecoration(
            hintText: 'Business Entity No.',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(5.0),
              borderSide: BorderSide.none,
            ),
            filled: true,
            fillColor: Colors.grey[200],
            contentPadding:
            const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0),
          ),
        ),
        const SizedBox(height: 16),
        Center( // 버튼 정렬
            child: TextButton( // 다음 단계 버튼
              onPressed: () {
                // TODO: Implement first next step action if needed
              },
              child: const Text(
                'To Next Step >>',
                style: TextStyle(color: Colors.black),
              ),
            ),
        ),
      ],
    );
  }
}