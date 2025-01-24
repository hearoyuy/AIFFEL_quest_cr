import 'package:flutter/material.dart';

void main() {
  runApp(MainApp());
}

class MainApp extends StatefulWidget {
  @override
  State<MainApp> createState() => _MainAppState();
}

class _MainAppState extends State<MainApp> {
  final _routerDelegate = MyRouterDelegate();
  final _routeInformationParser = MyRouteInformationParser();

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerDelegate: _routerDelegate,
      routeInformationParser: _routeInformationParser,
    );
  }
}

class RoutePath {
  final String? id;

  RoutePath.home() : id = null;
  RoutePath.detail(this.id);
}


class MyRouterDelegate extends RouterDelegate<RoutePath>
    with ChangeNotifier, PopNavigatorRouterDelegateMixin<RoutePath> {
  final GlobalKey<NavigatorState> navigatorKey;
  bool isCat = true;
  String? selectedId;

  MyRouterDelegate() : navigatorKey = GlobalKey<NavigatorState>();

  @override
  RoutePath get currentConfiguration {
    if (selectedId != null) {
      return RoutePath.detail(selectedId!);
    } else {
      return RoutePath.home();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Navigator(
      key: navigatorKey,
      pages: [
        MaterialPage(
          child: FirstPage(
            isCat: isCat,
            onNext: () {
              isCat = false;
              notifyListeners();
            },
          ),
        ),
        if (!isCat)
          MaterialPage(
            child: SecondPage(
              isCat: isCat,
              onBack: () {
                isCat = true;
                notifyListeners();
              },
            ),
          ),
      ],
      onPopPage: (route, result) {
        if (!route.didPop(result)) {
          return false;
        }
        selectedId = null;
        notifyListeners();
        return true;
      },
    );
  }
  @override
  Future<void> setNewRoutePath(configuration) async {}

}

class MyRouteInformationParser extends RouteInformationParser<RoutePath> {
  @override
  Future<RoutePath> parseRouteInformation(RouteInformation routeInformation) async {
    final uri = Uri.parse(routeInformation.location!);

    if (uri.pathSegments.isNotEmpty && uri.pathSegments[0] == 'detail') {
      final id = uri.pathSegments.length > 1 ? uri.pathSegments[1] : null;
      if (id != null) {
        return RoutePath.detail(id);
      }
    }
    return RoutePath.home();
  }

  @override
  RouteInformation? restoreRouteInformation(RoutePath configuration) {
    if (configuration.id != null) {
      return RouteInformation(location: '/detail/${configuration.id}');
    }
    return RouteInformation(location: '/');
  }
}



class FirstPage extends StatelessWidget {
  final bool isCat;
  final VoidCallback onNext;

  const FirstPage({required this.isCat, required this.onNext, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: Image.asset('image/cat.png'),
          onPressed: () {
            debugPrint('is_cat: $isCat');
          },
        ),
        title: Text('First Page'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          ElevatedButton(
            onPressed: onNext,
            child: Text('Next'),
          ),
          Spacer(),
          GestureDetector(
            onTap: () {
              debugPrint('is_cat: $isCat');
            },
            child: Image.asset('image/cat.png'),
          ),
          SizedBox(height: 30),
        ],
      ),
    );
  }
}
class SecondPage extends StatelessWidget {
  final bool isCat;
  final VoidCallback onBack;

  const SecondPage({required this.isCat, required this.onBack, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: Image.asset('image/dog.jpg'), // 강아지 이미지 아이콘
          onPressed: () {
            debugPrint('is_cat: $isCat');
          },
        ),
        title: Text('Second Page'),
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          ElevatedButton(
            onPressed: onBack,
            child: Text('Back'),
          ),
          Spacer(),
          GestureDetector(
            onTap: () {
              debugPrint('is_cat: $isCat');
            },
            child: Image.asset('image/dog.jpg', height: 300),
          ),
          SizedBox(height: 20),
        ],
      ),
    );
  }
}


// 회고
// 최창윤 : 