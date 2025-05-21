document.addEventListener("DOMContentLoaded", () => {
  const sidebar  = document.getElementById("sidebar");
  const mainWrap = document.getElementById("mainWrapper");
  const btnOpen  = document.getElementById("btnOpen");
  const btnClose = document.getElementById("btnClose");

  // 최초 로딩 시 화면 크기에 따라 사이드바 상태 결정
  const isMobile = window.innerWidth < 768;
  if (isMobile) {
    // 모바일: 사이드바 닫기
    sidebar.classList.add("-translate-x-full", "md:-translate-x-full");
    mainWrap.classList.remove("md:ml-64");
    btnOpen.classList.remove("hidden");
  } else {
    // 데스크톱: 사이드바 열기
    sidebar.classList.remove("-translate-x-full", "md:-translate-x-full");
    mainWrap.classList.add("md:ml-64");
    btnOpen.classList.add("hidden");
  }

  // 열기
  const show = () => {
    sidebar.classList.remove("-translate-x-full", "md:-translate-x-full");
    mainWrap.classList.add("md:ml-64");

    // 모바일·데스크톱 공통으로 숨김 처리 (hidden만)
    btnOpen.classList.add("hidden");
  };

  // 닫기
  const hide = () => {
    sidebar.classList.add("-translate-x-full", "md:-translate-x-full");
    mainWrap.classList.remove("md:ml-64");

    // 다시 표시: hidden만 제거, md:hidden 그대로 두면
    // 데스크톱에서도 버튼이 나타남
    btnOpen.classList.remove("hidden");
  };

  btnOpen.addEventListener("click", show);
  btnClose.addEventListener("click", hide);
});