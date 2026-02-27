import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
            } else {
                OnboardingView()
            }
        }
        .animation(.easeInOut, value: authManager.isAuthenticated)
    }
}

#Preview {
    ContentView()
        .environmentObject(AuthManager())
}
