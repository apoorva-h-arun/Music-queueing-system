-- Music Queue Manager - Seed Data
-- Sample data for testing and development

-- Insert sample songs
INSERT INTO songs (title, artist, album, duration, popularity, genre, release_year) VALUES
('Blinding Lights', 'The Weeknd', 'After Hours', 200, 95.5, 'Synth-pop', 2019),
('Shape of You', 'Ed Sheeran', '÷ (Divide)', 233, 92.3, 'Pop', 2017),
('Someone Like You', 'Adele', '21', 285, 88.7, 'Soul', 2011),
('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 354, 96.2, 'Rock', 1975),
('Hotel California', 'Eagles', 'Hotel California', 391, 90.1, 'Rock', 1976),
('Imagine', 'John Lennon', 'Imagine', 183, 89.5, 'Soft Rock', 1971),
('Billie Jean', 'Michael Jackson', 'Thriller', 294, 94.8, 'Pop', 1982),
('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 301, 91.2, 'Grunge', 1991),
('Rolling in the Deep', 'Adele', '21', 228, 93.4, 'Soul', 2010),
('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 482, 95.9, 'Rock', 1971),
('Sweet Child O'' Mine', 'Guns N'' Roses', 'Appetite for Destruction', 356, 92.7, 'Rock', 1987),
('Wonderwall', 'Oasis', '(What''s the Story) Morning Glory?', 258, 87.3, 'Rock', 1995),
('Hey Jude', 'The Beatles', 'Hey Jude', 431, 94.1, 'Rock', 1968),
('Lose Yourself', 'Eminem', '8 Mile Soundtrack', 326, 93.8, 'Hip Hop', 2002),
('Thriller', 'Michael Jackson', 'Thriller', 357, 95.3, 'Pop', 1982),
('Purple Rain', 'Prince', 'Purple Rain', 524, 91.6, 'Rock', 1984),
('November Rain', 'Guns N'' Roses', 'Use Your Illusion I', 537, 90.4, 'Rock', 1991),
('Hallelujah', 'Leonard Cohen', 'Various Positions', 272, 88.9, 'Folk', 1984),
('Don''t Stop Believin''', 'Journey', 'Escape', 251, 92.1, 'Rock', 1981),
('Comfortably Numb', 'Pink Floyd', 'The Wall', 382, 93.2, 'Progressive Rock', 1979),
('Levitating', 'Dua Lipa', 'Future Nostalgia', 203, 89.7, 'Disco Pop', 2020),
('Watermelon Sugar', 'Harry Styles', 'Fine Line', 174, 87.5, 'Pop Rock', 2019),
('Bad Guy', 'Billie Eilish', 'When We All Fall Asleep', 194, 91.8, 'Electropop', 2019),
('Circles', 'Post Malone', 'Hollywood''s Bleeding', 215, 88.3, 'Pop', 2019),
('Sunflower', 'Post Malone, Swae Lee', 'Spider-Man: Into the Spider-Verse', 158, 90.2, 'Hip Hop', 2018),
('Old Town Road', 'Lil Nas X', '7 EP', 113, 92.9, 'Country Rap', 2019),
('Señorita', 'Shawn Mendes, Camila Cabello', 'Shawn Mendes', 191, 89.1, 'Pop', 2019),
('Dance Monkey', 'Tones and I', 'The Kids Are Coming', 209, 88.6, 'Electropop', 2019),
('Memories', 'Maroon 5', 'Jordi', 189, 86.4, 'Pop', 2019),
('Believer', 'Imagine Dragons', 'Evolve', 204, 90.7, 'Alternative Rock', 2017);

-- Insert sample users
INSERT INTO users (name, email, premium) VALUES
('John Doe', 'john.doe@example.com', TRUE),
('Jane Smith', 'jane.smith@example.com', FALSE),
('Bob Johnson', 'bob.johnson@example.com', TRUE),
('Alice Williams', 'alice.williams@example.com', FALSE),
('Charlie Brown', 'charlie.brown@example.com', FALSE);

-- Insert sample play history
INSERT INTO play_history (song_id, user_id, duration_played, completed) VALUES
(1, 1, 200, TRUE),
(2, 1, 233, TRUE),
(3, 1, 150, FALSE),
(4, 2, 354, TRUE),
(5, 2, 391, TRUE),
(1, 2, 200, TRUE),
(6, 3, 183, TRUE),
(7, 3, 294, TRUE),
(8, 3, 301, TRUE),
(9, 4, 228, TRUE),
(10, 4, 482, TRUE),
(1, 4, 200, TRUE),
(11, 5, 356, TRUE),
(12, 5, 258, TRUE),
(13, 5, 431, TRUE),
(1, 5, 200, TRUE),
(14, 1, 326, TRUE),
(15, 2, 357, TRUE),
(16, 3, 524, TRUE),
(17, 4, 537, TRUE),
(18, 5, 272, TRUE);

-- Insert initial queue snapshot (optional)
INSERT INTO queue_snapshot (song_id, position, priority, is_current) VALUES
(1, 0, 95.5, TRUE),
(2, 1, 92.3, FALSE),
(4, 2, 96.2, FALSE),
(7, 3, 94.8, FALSE),
(10, 4, 95.9, FALSE);

-- Success message
SELECT 'Sample data inserted successfully!' AS status;
SELECT COUNT(*) AS total_songs FROM songs;
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(*) AS total_history FROM play_history;
