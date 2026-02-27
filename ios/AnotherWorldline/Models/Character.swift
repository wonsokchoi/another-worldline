import Foundation

struct GameCharacter: Codable, Identifiable {
    let id: String
    let name: String
    let race: String
    let stats: CharacterStats
    let skills: [String]
    let equipment: [String: String]
    let pets: [String]
    let relationships: [String]
    let rarityScore: Double
    let worldlineCount: Int
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, name, race, stats, skills, equipment, pets, relationships
        case rarityScore = "rarity_score"
        case worldlineCount = "worldline_count"
        case createdAt = "created_at"
    }
}

struct CharacterStats: Codable {
    let hp: Int
    let mp: Int
    let strength: Int
    let intelligence: Int
    let agility: Int
    let luck: Int
    let charm: Int
}
