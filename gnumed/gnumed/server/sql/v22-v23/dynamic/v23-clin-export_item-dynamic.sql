-- ==============================================================
-- GNUmed database schema change script
--
-- License: GPL v2 or later
-- Author: karsten.hilbert@gmx.net
--
-- ==============================================================
\set ON_ERROR_STOP 1
--set default_transaction_read_only to off;

set check_function_bodies to on;

-- --------------------------------------------------------------
-- convert PK to IDENTITY:

--alter table clin.export_item
--	alter column pk drop default;

--drop sequence if exists clin.export_item_pk_seq;

--alter table clin.export_item
--	alter column pk add generated by default as identity;

-- --------------------------------------------------------------
drop function if exists clin.get_next_export_item_list_position(IN _fk_identity integer) cascade;

create function clin.get_next_export_item_list_position(IN _fk_identity integer)
	returns integer
	language SQL
	as 'SELECT COALESCE(MAX(c_ei.list_position) + 1, 1) FROM clin.export_item c_ei WHERE c_ei.fk_identity = _fk_identity;'
;

comment on function clin.get_next_export_item_list_position(IN _fk_identity integer) is
	'Get the next list position for the given identity.';

-- --------------------------------------------------------------
-- add trigger as default
drop function if exists clin.trf_exp_item_set_list_pos_default() cascade;

create function clin.trf_exp_item_set_list_pos_default()
	returns trigger
	language plpgsql
	as '
BEGIN
	IF NEW.list_position IS NOT NULL THEN
		RETURN NEW;
	END IF;
	SELECT clin.get_next_export_item_list_position(NEW.fk_identity) INTO NEW.list_position;
	RETURN NEW;
END';

comment on function clin.trf_exp_item_set_list_pos_default() is
	'Set clin.export_item.list_postion to the "next" (max+1) value per-patient.';

create trigger tr_ins_upd_clin_exp_item_set_list_pos_default
	before insert or update on
		clin.export_item
	for
		each row
	execute procedure
		clin.trf_exp_item_set_list_pos_default();

-- --------------------------------------------------------------
-- update list_position to default (that is, populate it)
update clin.export_item c_ei set
	list_position = DEFAULT
where list_position IS NULL;

-- --------------------------------------------------------------
alter table clin.export_item
	alter column list_position set not null;

comment on column clin.export_item.list_position is
	'This is the per-identity list position for this export item.';


alter table clin.export_item
	drop constraint if exists clin_export_item_uniq_list_pos_per_identity cascade;

alter table clin.export_item
	add constraint clin_export_item_uniq_list_pos_per_identity
		unique(fk_identity, list_position);


alter table clin.export_item
	drop constraint if exists clin_export_item_sane_list_pos cascade;

alter table clin.export_item
	add constraint clin_export_item_sane_list_pos
		check (list_position > 0);

-- --------------------------------------------------------------
drop function if exists clin.export_item_set_list_position(IN _pk INT, IN _target_position INT) cascade;

create function clin.export_item_set_list_position(IN _pk INT, IN _target_position INT)
	returns bool
	language plpgsql
	as '
DECLARE
	_pk_exists bool;
	_target_pos_exists bool;
	_current_pos integer;
	_target_identity integer;
BEGIN
	-- target position must be positive integer
	IF _target_position < 0 THEN
		RAISE EXCEPTION
			''[clin.export_item_set_list_position] - target position negative: %'', _target_position
			USING ERRCODE = ''check_violation''
		;
		RETURN FALSE;
	END IF;
	-- check that item exists
	SELECT EXISTS(SELECT 1 FROM clin.export_item WHERE pk = _pk) INTO _pk_exists;
	IF _pk_exists IS DISTINCT FROM TRUE THEN
		RAISE EXCEPTION
			''[clin.export_item_set_list_position] - export item not found: %'', _pk
			USING ERRCODE = ''check_violation''
		;
		RETURN FALSE;
	END IF;
	-- anything to do ?
	SELECT list_position INTO _current_pos FROM clin.export_item WHERE pk = _pk;
	IF _current_pos = _target_position THEN
		RAISE NOTICE ''[clin.export_item_set_list_position] item % already at pos %'', _pk, _target_position;
		RETURN TRUE;
	END IF;

	-- get patient
	SELECT fk_identity INTO _target_identity FROM clin.export_item WHERE pk = _pk;
	-- target position already exists ?
	SELECT EXISTS (
		SELECT 1 FROM clin.export_item
		WHERE
			fk_identity = _target_identity
				AND
			list_position = _target_position
	) INTO _target_pos_exists;
	--- move rows that are "in the way"
	IF _target_pos_exists IS TRUE THEN
		WITH cte AS (
			SELECT pk, list_position
			FROM clin.export_item
			WHERE
				list_position >= _target_position
					AND
				fk_identity = _target_identity
			ORDER BY
				list_position DESC
		)
		UPDATE clin.export_item SET
			list_position = cte.list_position + 1
		FROM cte
		WHERE
			clin.export_item.pk = cte.pk;
	END IF;
	--- now update the item
	UPDATE clin.export_item SET list_position = _target_position WHERE pk = _pk;

	RETURN TRUE;
END;';

comment on function clin.export_item_set_list_position(IN _pk INT, IN _target_position INT) is
	'Set clin.export_item.list_position to _target_position for the row with pk = _pk. If a row with this list_position for this identity already exists, the list_position of all rows with this or a higher list_position are incremented. This will fail, once MAXINT is reached (per identity), which is rather unlikely, however.';

-- --------------------------------------------------------------
select gm.log_script_insertion('v23-clin-export_item-dynamic.sql', '23.0');