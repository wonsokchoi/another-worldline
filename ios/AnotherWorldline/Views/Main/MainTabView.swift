import SwiftUI

struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            WorldlineHomeView()
                .tabItem {
                    Image(systemName: "globe")
                    Text("세계선")
                }
                .tag(0)

            CharacterView()
                .tabItem {
                    Image(systemName: "person.fill")
                    Text("캐릭터")
                }
                .tag(1)

            RankingView()
                .tabItem {
                    Image(systemName: "trophy.fill")
                    Text("랭킹")
                }
                .tag(2)
        }
        .tint(.cyan)
    }
}

#Preview {
    MainTabView()
}
