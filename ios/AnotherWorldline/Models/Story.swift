import Foundation

struct Story: Codable, Identifiable {
    let id: String
    let genre: String
    let content: String
    let worldlineNumber: Int
    let sequenceNumber: Int
    let statChanges: [String: Int]?
    let itemsGained: [String: Any]?
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, genre, content
        case worldlineNumber = "worldline_number"
        case sequenceNumber = "sequence_number"
        case statChanges = "stat_changes"
        case createdAt = "created_at"
    }

    // Custom decoding to handle itemsGained as Any
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decode(String.self, forKey: .id)
        genre = try container.decode(String.self, forKey: .genre)
        content = try container.decode(String.self, forKey: .content)
        worldlineNumber = try container.decode(Int.self, forKey: .worldlineNumber)
        sequenceNumber = try container.decode(Int.self, forKey: .sequenceNumber)
        statChanges = try container.decodeIfPresent([String: Int].self, forKey: .statChanges)
        createdAt = try container.decode(String.self, forKey: .createdAt)
        itemsGained = nil  // Handle separately if needed
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(genre, forKey: .genre)
        try container.encode(content, forKey: .content)
        try container.encode(worldlineNumber, forKey: .worldlineNumber)
        try container.encode(sequenceNumber, forKey: .sequenceNumber)
        try container.encodeIfPresent(statChanges, forKey: .statChanges)
        try container.encode(createdAt, forKey: .createdAt)
    }
}

struct StoryHistory: Codable {
    let stories: [Story]
    let total: Int
}
