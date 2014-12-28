BEGIN TRANSACTION;
CREATE TABLE meta (id INTEGER PRIMARY KEY, book_id NUMERIC, desc_id NUMERIC, data_id NUMERIC,
				   FOREIGN KEY (book_id) REFERENCES books(id),
				   FOREIGN KEY (desc_id) REFERENCES desc(id),
				   FOREIGN KEY (data_id) REFERENCES data(id));
CREATE TABLE desc (id INTEGER PRIMARY KEY, name TEXT);
INSERT INTO `desc` VALUES(1,'author');
INSERT INTO `desc` VALUES(2,'genre');
INSERT INTO `desc` VALUES(3,'sequence');
CREATE TABLE data (id INTEGER PRIMARY KEY, data TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, ext TEXT, title TEXT, path TEXT);
CREATE INDEX `desc_id_index` ON `meta` (`desc_id` ASC);
COMMIT;
