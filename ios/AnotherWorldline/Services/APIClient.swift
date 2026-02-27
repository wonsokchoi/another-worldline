import Foundation

enum APIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError
    case serverError(String)
    case unauthorized
    case tooManyRequests(String)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .noData: return "No data received"
        case .decodingError: return "Failed to decode response"
        case .serverError(let msg): return msg
        case .unauthorized: return "Please login again"
        case .tooManyRequests(let msg): return msg
        }
    }
}

class APIClient {
    static let shared = APIClient()

    #if DEBUG
    private let baseURL = "http://localhost:8000"
    #else
    private let baseURL = "https://api.another-worldline.com"
    #endif

    private var token: String? {
        get { UserDefaults.standard.string(forKey: "auth_token") }
        set { UserDefaults.standard.set(newValue, forKey: "auth_token") }
    }

    var isAuthenticated: Bool {
        token != nil
    }

    func setToken(_ token: String) {
        self.token = token
    }

    func clearToken() {
        self.token = nil
    }

    // MARK: - Auth

    func register(phoneNumber: String) async throws -> [String: Any] {
        let body = ["phone_number": phoneNumber]
        return try await post(path: "/auth/register", body: body)
    }

    func verify(phoneNumber: String, code: String) async throws -> String {
        let body = ["phone_number": phoneNumber, "code": code]
        let result: [String: Any] = try await post(path: "/auth/verify", body: body)
        guard let token = result["access_token"] as? String else {
            throw APIError.decodingError
        }
        setToken(token)
        return token
    }

    // MARK: - Characters

    func createCharacter(name: String) async throws -> GameCharacter {
        let body = ["name": name]
        return try await postDecodable(path: "/characters", body: body)
    }

    func getCharacter(id: String) async throws -> GameCharacter {
        return try await getDecodable(path: "/characters/\(id)")
    }

    // MARK: - Stories

    func pullStory(characterId: String) async throws -> Story {
        let body = ["character_id": characterId]
        return try await postDecodable(path: "/stories/pull", body: body)
    }

    func getStoryHistory(characterId: String, limit: Int = 20, offset: Int = 0) async throws -> StoryHistory {
        return try await getDecodable(path: "/stories/\(characterId)/history?limit=\(limit)&offset=\(offset)")
    }

    // MARK: - Rankings

    func getRankings(limit: Int = 50) async throws -> RankingResponse {
        return try await getDecodable(path: "/rankings?limit=\(limit)")
    }

    // MARK: - Private helpers

    private func request(path: String, method: String, body: Data? = nil) async throws -> Data {
        guard let url = URL(string: baseURL + path) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        request.httpBody = body

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.noData
        }

        switch httpResponse.statusCode {
        case 200...299:
            return data
        case 401:
            throw APIError.unauthorized
        case 429:
            let detail = try? JSONDecoder().decode([String: String].self, from: data)
            throw APIError.tooManyRequests(detail?["detail"] ?? "Too many requests")
        default:
            let detail = try? JSONDecoder().decode([String: String].self, from: data)
            throw APIError.serverError(detail?["detail"] ?? "Server error")
        }
    }

    private func post(path: String, body: [String: Any]) async throws -> [String: Any] {
        let jsonData = try JSONSerialization.data(withJSONObject: body)
        let data = try await request(path: path, method: "POST", body: jsonData)
        guard let result = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw APIError.decodingError
        }
        return result
    }

    private func postDecodable<T: Decodable>(path: String, body: [String: Any]) async throws -> T {
        let jsonData = try JSONSerialization.data(withJSONObject: body)
        let data = try await request(path: path, method: "POST", body: jsonData)
        return try JSONDecoder().decode(T.self, from: data)
    }

    private func getDecodable<T: Decodable>(path: String) async throws -> T {
        let data = try await request(path: path, method: "GET")
        return try JSONDecoder().decode(T.self, from: data)
    }
}
