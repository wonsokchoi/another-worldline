import SwiftUI

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?

    private let api = APIClient.shared

    init() {
        isAuthenticated = api.isAuthenticated
    }

    func register(phoneNumber: String) async throws -> String {
        let result = try await api.register(phoneNumber: phoneNumber)
        return result["dev_code"] as? String ?? ""
    }

    func verify(phoneNumber: String, code: String) async throws {
        _ = try await api.verify(phoneNumber: phoneNumber, code: code)
        isAuthenticated = true
    }

    func logout() {
        api.clearToken()
        isAuthenticated = false
        currentUser = nil
    }
}
