import 'package:flutter/material.dart';
import 'document_portal_screen.dart'; // ViewState enum 사용을 위해 임포트

class CustomBottomBar extends StatelessWidget {
  final ViewState currentViewState; // 현재 화면 주요 상태

  // Business Counterparty 선택 시 필요한 콜백 함수들 추가
  final VoidCallback? onAddDocumentsPressed; // "Add Documents" 버튼 콜백
  final VoidCallback? onExitPressed; // "Exit" 버튼 콜백
  final VoidCallback? onToNextStepPressed; // "To Next Step >>" 버튼 콜백 (상세 폼에서 사용)


  const CustomBottomBar({
    Key? key,
    required this.currentViewState,
    // Business Counterparty 선택 시 필요한 콜백들은 nullable로 선언 (다른 ViewState에서는 null일 수 있음)
    this.onAddDocumentsPressed,
    this.onExitPressed,
    this.onToNextStepPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // ViewState에 따라 다른 버튼 레이아웃 반환
    if (currentViewState == ViewState.employee) {
      // Employee 선택 시 하단 버튼들 (Confirm & Submit 등)
      return BottomAppBar(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Expanded( // Expanded로 감싸서 공간을 균등하게 사용
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0), // 버튼 간 간격
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Confirm & Submit 액션 구현
                      print("Confirm & Submit pressed");
                    },
                    style: ElevatedButton.styleFrom(
                      // minimumSize: const Size(140, 48), // Expanded 사용 시 minimumSize는 덜 중요
                      backgroundColor: Colors.grey[800],
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold), // 텍스트 크기 조정
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                    ),
                    child: const Text('Confirm & Submit', textAlign: TextAlign.center), // 텍스트 가운데 정렬
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Confirm & Reject 액션 구현
                      print("Confirm & Reject pressed");
                    },
                    style: ElevatedButton.styleFrom(
                      // minimumSize: const Size(140, 48),
                      backgroundColor: Colors.grey[800],
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                    ),
                    child: const Text('Confirm & Reject', textAlign: TextAlign.center),
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Change 액션 구현
                      print("Change pressed");
                    },
                    style: ElevatedButton.styleFrom(
                      // minimumSize: const Size(100, 48),
                      backgroundColor: Colors.grey[800],
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                    ),
                    child: const Text('Change', textAlign: TextAlign.center),
                  ),
                ),
              ),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: ElevatedButton(
                    onPressed: () {
                      // TODO: Delete 액션 구현
                      print("Delete pressed");
                    },
                    style: ElevatedButton.styleFrom(
                      // minimumSize: const Size(100, 48),
                      backgroundColor: Colors.grey[800],
                      foregroundColor: Colors.white,
                      textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                    ),
                    child: const Text('Delete', textAlign: TextAlign.center),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    } else if (currentViewState == ViewState.businessCounterparty) {
      // Business Counterparty 선택 시 하단 버튼들 (To Next Step, Add Documents, Exit)
      return BottomAppBar(
        child: Padding(
          // vertical 패딩 값을 0.0으로 설정하여 버튼 그룹 전체를 위로 이동
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 0.0), // vertical: 4.0 -> 0.0
          child: Column( // Use Column for stacking
            mainAxisSize: MainAxisSize.min, // Take minimum vertical space
            crossAxisAlignment: CrossAxisAlignment.center, // Center children horizontally
            children: [
              // "To Next Step >>" button (TextButton)
              TextButton(
                onPressed: onToNextStepPressed, // Pass the callback
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: const Text(
                  'To Next Step >>',
                  style: TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
              const SizedBox(height: 12), // 버튼과 아래 Row 간 간격

              // "Add Documents"와 "Exit" 버튼을 담는 Row
              Row( // Use Row for side-by-side buttons
                mainAxisAlignment: MainAxisAlignment.center, // Row 내부 버튼들을 가운데 정렬
                children: [
                  // "Add Documents" button (ElevatedButton)
                  Expanded( // Use Expanded to make buttons share horizontal space
                    child: Padding( // Add padding around the button
                      padding: const EdgeInsets.symmetric(horizontal: 8.0), // Adjust horizontal padding
                      child: ElevatedButton(
                        onPressed: onAddDocumentsPressed, // Pass the callback
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[800],
                          foregroundColor: Colors.white,
                          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 15), // Ensure consistent vertical padding
                        ),
                        child: const Text('Add Documents', textAlign: TextAlign.center), // Center text
                      ),
                    ),
                  ),
                  // "Exit" button (ElevatedButton)
                  Expanded( // Use Expanded for the second button too
                    child: Padding( // Add padding around the button
                      padding: const EdgeInsets.symmetric(horizontal: 8.0), // Adjust horizontal padding
                      child: ElevatedButton(
                        onPressed: onExitPressed, // Pass the callback
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.grey[800],
                          foregroundColor: Colors.white,
                          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8.0),
                          ),
                          padding: const EdgeInsets.symmetric(vertical: 15), // Ensure consistent vertical padding
                        ),
                        child: const Text('Exit', textAlign: TextAlign.center), // Center text
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    } else {
      // 초기 상태일 때는 빈 공간 반환
      return const SizedBox.shrink();
    }
  }
}
