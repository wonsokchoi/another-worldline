import Foundation

struct RankingEntry: Codable, Identifiable {
    var id: Int { rank }
    let rank: Int
    let characterName: String
    let userNickname: String?
    let rarityScore: Double
    let worldlineCount: Int
    let race: String

    enum CodingKeys: String, CodingKey {
        case rank, race
        case characterName = "character_name"
        case userNickname = "user_nickname"
        case rarityScore = "rarity_score"
        case worldlineCount = "worldline_count"
    }
}

struct RankingResponse: Codable {
    let rankings: [RankingEntry]
    let totalCharacters: Int
    let myRank: Int?

    enum CodingKeys: String, CodingKey {
        case rankings
        case totalCharacters = "total_characters"
        case myRank = "my_rank"
    }
}
