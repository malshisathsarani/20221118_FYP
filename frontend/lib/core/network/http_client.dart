import 'package:dio/dio.dart';
import '../config/api_config.dart';
import '../utils/storage_helper.dart';

class HttpClient {
  static final HttpClient _instance = HttpClient._internal();
  factory HttpClient() => _instance;

  late Dio dio;

  HttpClient._internal() {
    dio = Dio(
      BaseOptions(
        baseUrl: ApiConfig.baseUrl,
        connectTimeout: ApiConfig.connectionTimeout,
        receiveTimeout: ApiConfig.receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token to requests
          final token = await StorageHelper.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          // Handle token expiration
          if (error.response?.statusCode == 401) {
            // Token expired, try to refresh
            try {
              await _refreshToken();
              // Retry the original request
              return handler.resolve(await _retry(error.requestOptions));
            } catch (e) {
              // Refresh failed, logout user
              await StorageHelper.clearAll();
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<Response> _retry(RequestOptions requestOptions) async {
    final options = Options(
      method: requestOptions.method,
      headers: requestOptions.headers,
    );
    return dio.request(
      requestOptions.path,
      data: requestOptions.data,
      queryParameters: requestOptions.queryParameters,
      options: options,
    );
  }

  Future<void> _refreshToken() async {
    final refreshToken = await StorageHelper.getRefreshToken();
    if (refreshToken == null) throw Exception('No refresh token');

    final response = await dio.post(
      ApiConfig.refreshToken,
      queryParameters: {'refresh_token': refreshToken},
    );

    if (response.statusCode == 200) {
      await StorageHelper.saveAccessToken(response.data['access_token']);
      await StorageHelper.saveRefreshToken(response.data['refresh_token']);
    }
  }
}
