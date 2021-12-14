create function create_database()
	returns void language sql as $$
		create table if not exists "Student"(
			name text primary key not null,
			studentID text not null,
			lastUpdate timestamptz default current_timestamp not null
		);
		create table if not exists "LabWork"(
			id integer primary key not null generated always as identity,
			title text not null,
			discipline text not null,
			student text not null
		);
		create index if not exists student on "LabWork" (student);
        create or replace function update_time()
			returns trigger as $u$
			begin
				new.lastUpdate = current_timestamp;
				return new;
			end;
		$u$ language plpgsql;

		drop trigger if exists trigger_update on "Student";

		create trigger trigger_update before update on "Student"
			for row execute procedure update_time();
$$;

select "create_database"();

create function get_publishers()
	returns json language plpgsql as $$
		begin
			return (select json_agg(json_build_object(
				'name', "Student".name,
				'studentID', "Student".studentID,
				'lastUpdate', "Student".lastUpdate
				)) from "Student");
		end
	$$;

create function get_books()
	returns json language plpgsql as $$
		begin
			return (select json_agg(json_build_object(
				'id', "LabWork".id,
				'title', "LabWork".title,
				'discipline', "LabWork".discipline,
				'student', "LabWork".student
				)) from "LabWork");
		end
	$$;

create function add_to_publisher(in name text, in studentID text)
	returns void language sql as $$
		insert into "Student"(name, studentID) values (name, studentID)
	$$;

create function add_to_book(in title text, in discipline text, in student text)
	returns void language sql as $$
		insert into "LabWork"(title, discipline, student) values (title, discipline, student)
	$$;

create function clear_publishers()
	returns void language sql as $$
		truncate "Student"
	$$;

create function clear_books()
	returns void language sql as $$
		truncate "LabWork"
	$$;

create function clear_all()
	returns void language sql as $$
		truncate "Student";
		truncate "LabWork"
	$$;

create function find_book(in query text)
	returns json language plpgsql as $$
		begin
			return (select json_agg(json_build_object(
				'id', "LabWork".id,
				'title', "LabWork".title,
				'discipline', "LabWork".discipline,
				'student', "LabWork".student
				)) from "LabWork" where "LabWork".student like concat('%', query, '%'));
		end;
	$$;

create function find_publisher(in query text)
	returns json language plpgsql as $$
		begin
			return (select json_agg(json_build_object(
				'name', "Student".name,
				'studentID', "Student".studentID,
				'lastUpdate', "Student".lastUpdate
				)) from "Student" where "Student".studentID in (
					select "LabWork".student from "LabWork" where "LabWork".student LIKE concat('%', query, '%')
				)
			);
		end;
	$$;

create function delete_book_by_author(in auth text)
	returns void language plpgsql as $$
		begin
			delete from "LabWork" where student = auth;
		end;
	$$;

create function delete_publisher_record(in id text)
	returns void language plpgsql as $$
		begin
			delete from "Student" where studentID = id;
		end;
	$$;

create function delete_book_record(in id_ integer)
	returns void language plpgsql as $$
		begin
			delete from "LabWork" where id = id_;
		end;
	$$;

create function update_publisher_by_name(in newname text, in id text)
	returns void language plpgsql as $$
		begin
			update "Student" set name = newname where name = id;
		end;
	$$;

create function update_publisher_by_tel(in newtel text, in id text)
	returns void language plpgsql as $$
		begin
			update "Student" set studentID = newtel where name = id;
		end;
	$$;

create function update_book_by_title(in newtitle text, in id_ integer)
	returns void language plpgsql as $$
		begin
			update "LabWork" set title = newtitle where id = id_;
		end;
	$$;

create function update_book_by_author(in newauthor text, in id_ integer)
	returns void language plpgsql as $$
		begin
			update "LabWork" set discipline = newauthor where id = id_;
		end;
	$$;

create function update_book_by_publisher(in newpublisher text, in id_ integer)
	returns void language plpgsql as $$
		begin
			update "LabWork" set student = newpublisher where id = id_;
		end;
	$$;