--
-- PostgreSQL database dump
--

\restrict IgbTwTFln2QVBvXtat4CDFZUld1rK8kl4djVPCVDqeaW9xXkkG9zyaDK2AcFAd0

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-10-31 19:43:02

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 38068)
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    attendance_id integer NOT NULL,
    lesson_id integer NOT NULL,
    student_id integer NOT NULL,
    mark character varying(30) NOT NULL,
    attendance_date date,
    CONSTRAINT attendance_mark_check CHECK (((mark)::text = ANY (ARRAY[('Присутствовал'::character varying)::text, ('Отсутствовал'::character varying)::text, ('Уважительная причина'::character varying)::text])))
);


ALTER TABLE public.attendance OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 38076)
-- Name: attendance_attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_attendance_id_seq OWNER TO postgres;

--
-- TOC entry 5168 (class 0 OID 0)
-- Dependencies: 220
-- Name: attendance_attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_attendance_id_seq OWNED BY public.attendance.attendance_id;


--
-- TOC entry 221 (class 1259 OID 38077)
-- Name: curators; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.curators (
    curator_id integer NOT NULL,
    employee_id integer,
    group_id integer,
    discipline_id integer
);


ALTER TABLE public.curators OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 38081)
-- Name: curators_curator_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.curators_curator_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.curators_curator_id_seq OWNER TO postgres;

--
-- TOC entry 5169 (class 0 OID 0)
-- Dependencies: 222
-- Name: curators_curator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.curators_curator_id_seq OWNED BY public.curators.curator_id;


--
-- TOC entry 223 (class 1259 OID 38082)
-- Name: data_quality_notes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_quality_notes (
    note_id integer NOT NULL,
    category character varying(100),
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.data_quality_notes OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 38089)
-- Name: data_quality_notes_note_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_quality_notes_note_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_quality_notes_note_id_seq OWNER TO postgres;

--
-- TOC entry 5170 (class 0 OID 0)
-- Dependencies: 224
-- Name: data_quality_notes_note_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_quality_notes_note_id_seq OWNED BY public.data_quality_notes.note_id;


--
-- TOC entry 225 (class 1259 OID 38090)
-- Name: disciplines; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disciplines (
    discipline_id integer NOT NULL,
    name character varying(100) NOT NULL,
    price numeric(10,2) DEFAULT 0 NOT NULL,
    teacher_id integer,
    classroom character varying(100)
);


ALTER TABLE public.disciplines OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 38097)
-- Name: disciplines_discipline_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.disciplines_discipline_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.disciplines_discipline_id_seq OWNER TO postgres;

--
-- TOC entry 5171 (class 0 OID 0)
-- Dependencies: 226
-- Name: disciplines_discipline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.disciplines_discipline_id_seq OWNED BY public.disciplines.discipline_id;


--
-- TOC entry 227 (class 1259 OID 38098)
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    employee_id integer NOT NULL,
    surname character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    third_name character varying(100),
    phone character varying(20),
    email character varying(100),
    login character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 38109)
-- Name: employees_employee_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_employee_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_employee_id_seq OWNER TO postgres;

--
-- TOC entry 5172 (class 0 OID 0)
-- Dependencies: 228
-- Name: employees_employee_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_employee_id_seq OWNED BY public.employees.employee_id;


--
-- TOC entry 229 (class 1259 OID 38110)
-- Name: grades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.grades (
    grade_id integer NOT NULL,
    student_id integer NOT NULL,
    discipline_id integer NOT NULL,
    grade_date date NOT NULL,
    value integer NOT NULL,
    CONSTRAINT grades_value_check CHECK (((value >= 1) AND (value <= 5)))
);


ALTER TABLE public.grades OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 38119)
-- Name: grades_grade_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.grades_grade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.grades_grade_id_seq OWNER TO postgres;

--
-- TOC entry 5173 (class 0 OID 0)
-- Dependencies: 230
-- Name: grades_grade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.grades_grade_id_seq OWNED BY public.grades.grade_id;


--
-- TOC entry 231 (class 1259 OID 38120)
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    group_id integer NOT NULL,
    name character varying(100) NOT NULL,
    year integer NOT NULL,
    teacher_id integer,
    curator_id integer
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 38126)
-- Name: groups_group_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.groups_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.groups_group_id_seq OWNER TO postgres;

--
-- TOC entry 5174 (class 0 OID 0)
-- Dependencies: 232
-- Name: groups_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.groups_group_id_seq OWNED BY public.groups.group_id;


--
-- TOC entry 233 (class 1259 OID 38127)
-- Name: lessons; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lessons (
    lesson_id integer NOT NULL,
    lesson_date date NOT NULL,
    lesson_time time without time zone NOT NULL,
    classroom character varying(50),
    group_id integer NOT NULL,
    teacher_id integer NOT NULL,
    discipline_id integer NOT NULL,
    duration_hours numeric(5,2) DEFAULT 2
);


ALTER TABLE public.lessons OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 38137)
-- Name: lessons_lesson_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.lessons_lesson_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.lessons_lesson_id_seq OWNER TO postgres;

--
-- TOC entry 5175 (class 0 OID 0)
-- Dependencies: 234
-- Name: lessons_lesson_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.lessons_lesson_id_seq OWNED BY public.lessons.lesson_id;


--
-- TOC entry 235 (class 1259 OID 38138)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    payment_id integer NOT NULL,
    student_id integer,
    payment_date date DEFAULT CURRENT_DATE NOT NULL,
    period character varying(30) NOT NULL,
    amount numeric(12,2) NOT NULL,
    method character varying(50) DEFAULT 'Наличные'::character varying NOT NULL,
    note text,
    CONSTRAINT payments_amount_check CHECK ((amount >= (0)::numeric))
);


ALTER TABLE public.payments OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 38151)
-- Name: payments_payment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_payment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payments_payment_id_seq OWNER TO postgres;

--
-- TOC entry 5176 (class 0 OID 0)
-- Dependencies: 236
-- Name: payments_payment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_payment_id_seq OWNED BY public.payments.payment_id;


--
-- TOC entry 237 (class 1259 OID 38152)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    role_id integer NOT NULL,
    name character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 38157)
-- Name: roles_role_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_role_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_role_id_seq OWNER TO postgres;

--
-- TOC entry 5177 (class 0 OID 0)
-- Dependencies: 238
-- Name: roles_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;


--
-- TOC entry 239 (class 1259 OID 38158)
-- Name: school_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.school_migrations (
    migration_key character varying(100) NOT NULL
);


ALTER TABLE public.school_migrations OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 38162)
-- Name: student_accounts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.student_accounts (
    account_id integer NOT NULL,
    student_id integer,
    login character varying(100) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.student_accounts OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 38168)
-- Name: student_accounts_account_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.student_accounts_account_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_accounts_account_id_seq OWNER TO postgres;

--
-- TOC entry 5178 (class 0 OID 0)
-- Dependencies: 241
-- Name: student_accounts_account_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.student_accounts_account_id_seq OWNED BY public.student_accounts.account_id;


--
-- TOC entry 242 (class 1259 OID 38169)
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    student_id integer NOT NULL,
    surname character varying(100) NOT NULL,
    name character varying(100) NOT NULL,
    third_name character varying(100),
    birth_date date,
    phone character varying(20),
    group_id integer NOT NULL
);


ALTER TABLE public.students OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 38176)
-- Name: students_student_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_student_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_student_id_seq OWNER TO postgres;

--
-- TOC entry 5179 (class 0 OID 0)
-- Dependencies: 243
-- Name: students_student_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_student_id_seq OWNED BY public.students.student_id;


--
-- TOC entry 244 (class 1259 OID 38177)
-- Name: v_attendance_report; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_attendance_report AS
 SELECT students.surname,
    students.name,
    lessons.lesson_date,
    lessons.lesson_time,
    disciplines.name AS discipline,
    attendance.mark
   FROM (((public.attendance
     JOIN public.students ON ((attendance.student_id = students.student_id)))
     JOIN public.lessons ON ((attendance.lesson_id = lessons.lesson_id)))
     JOIN public.disciplines ON ((lessons.discipline_id = disciplines.discipline_id)));


ALTER VIEW public.v_attendance_report OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 38182)
-- Name: v_schedule; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_schedule AS
 SELECT l.lesson_date,
    l.lesson_time,
    l.classroom,
    g.name AS group_name,
    e.surname AS teacher_surname,
    e.name AS teacher_name,
    d.name AS discipline
   FROM (((public.lessons l
     JOIN public.groups g ON ((l.group_id = g.group_id)))
     JOIN public.employees e ON ((l.teacher_id = e.employee_id)))
     JOIN public.disciplines d ON ((l.discipline_id = d.discipline_id)));


ALTER VIEW public.v_schedule OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 38187)
-- Name: v_student_grades; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_student_grades AS
 SELECT students.student_id,
    students.surname,
    students.name,
    disciplines.name AS discipline,
    grades.grade_date,
    grades.value AS grade
   FROM ((public.grades
     JOIN public.students ON ((grades.student_id = students.student_id)))
     JOIN public.disciplines ON ((grades.discipline_id = disciplines.discipline_id)));


ALTER VIEW public.v_student_grades OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 38191)
-- Name: weekly_schedule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.weekly_schedule (
    schedule_id integer NOT NULL,
    group_id integer NOT NULL,
    weekday integer NOT NULL,
    lesson_time time without time zone NOT NULL,
    discipline_id integer,
    teacher_id integer,
    classroom character varying(100),
    duration_hours numeric(5,2) DEFAULT 2 NOT NULL,
    CONSTRAINT weekly_schedule_weekday_check CHECK (((weekday >= 1) AND (weekday <= 7)))
);


ALTER TABLE public.weekly_schedule OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 38201)
-- Name: weekly_schedule_schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.weekly_schedule_schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.weekly_schedule_schedule_id_seq OWNER TO postgres;

--
-- TOC entry 5180 (class 0 OID 0)
-- Dependencies: 248
-- Name: weekly_schedule_schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.weekly_schedule_schedule_id_seq OWNED BY public.weekly_schedule.schedule_id;


--
-- TOC entry 4932 (class 2604 OID 38202)
-- Name: attendance attendance_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN attendance_id SET DEFAULT nextval('public.attendance_attendance_id_seq'::regclass);


--
-- TOC entry 4933 (class 2604 OID 38203)
-- Name: curators curator_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curators ALTER COLUMN curator_id SET DEFAULT nextval('public.curators_curator_id_seq'::regclass);


--
-- TOC entry 4934 (class 2604 OID 38204)
-- Name: data_quality_notes note_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_notes ALTER COLUMN note_id SET DEFAULT nextval('public.data_quality_notes_note_id_seq'::regclass);


--
-- TOC entry 4936 (class 2604 OID 38205)
-- Name: disciplines discipline_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disciplines ALTER COLUMN discipline_id SET DEFAULT nextval('public.disciplines_discipline_id_seq'::regclass);


--
-- TOC entry 4938 (class 2604 OID 38206)
-- Name: employees employee_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN employee_id SET DEFAULT nextval('public.employees_employee_id_seq'::regclass);


--
-- TOC entry 4939 (class 2604 OID 38207)
-- Name: grades grade_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades ALTER COLUMN grade_id SET DEFAULT nextval('public.grades_grade_id_seq'::regclass);


--
-- TOC entry 4940 (class 2604 OID 38208)
-- Name: groups group_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups ALTER COLUMN group_id SET DEFAULT nextval('public.groups_group_id_seq'::regclass);


--
-- TOC entry 4941 (class 2604 OID 38209)
-- Name: lessons lesson_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons ALTER COLUMN lesson_id SET DEFAULT nextval('public.lessons_lesson_id_seq'::regclass);


--
-- TOC entry 4943 (class 2604 OID 38210)
-- Name: payments payment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN payment_id SET DEFAULT nextval('public.payments_payment_id_seq'::regclass);


--
-- TOC entry 4946 (class 2604 OID 38211)
-- Name: roles role_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);


--
-- TOC entry 4947 (class 2604 OID 38212)
-- Name: student_accounts account_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_accounts ALTER COLUMN account_id SET DEFAULT nextval('public.student_accounts_account_id_seq'::regclass);


--
-- TOC entry 4948 (class 2604 OID 38213)
-- Name: students student_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN student_id SET DEFAULT nextval('public.students_student_id_seq'::regclass);


--
-- TOC entry 4949 (class 2604 OID 38214)
-- Name: weekly_schedule schedule_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule ALTER COLUMN schedule_id SET DEFAULT nextval('public.weekly_schedule_schedule_id_seq'::regclass);


--
-- TOC entry 4956 (class 2606 OID 38216)
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (attendance_id);


--
-- TOC entry 4958 (class 2606 OID 38218)
-- Name: curators curators_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curators
    ADD CONSTRAINT curators_pkey PRIMARY KEY (curator_id);


--
-- TOC entry 4960 (class 2606 OID 38220)
-- Name: data_quality_notes data_quality_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_quality_notes
    ADD CONSTRAINT data_quality_notes_pkey PRIMARY KEY (note_id);


--
-- TOC entry 4962 (class 2606 OID 38222)
-- Name: disciplines disciplines_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disciplines
    ADD CONSTRAINT disciplines_name_key UNIQUE (name);


--
-- TOC entry 4964 (class 2606 OID 38224)
-- Name: disciplines disciplines_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disciplines
    ADD CONSTRAINT disciplines_pkey PRIMARY KEY (discipline_id);


--
-- TOC entry 4966 (class 2606 OID 38226)
-- Name: employees employees_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_login_key UNIQUE (login);


--
-- TOC entry 4968 (class 2606 OID 38228)
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (employee_id);


--
-- TOC entry 4970 (class 2606 OID 38230)
-- Name: grades grades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_pkey PRIMARY KEY (grade_id);


--
-- TOC entry 4972 (class 2606 OID 38232)
-- Name: groups groups_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_name_key UNIQUE (name);


--
-- TOC entry 4974 (class 2606 OID 38234)
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (group_id);


--
-- TOC entry 4976 (class 2606 OID 38236)
-- Name: lessons lessons_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_pkey PRIMARY KEY (lesson_id);


--
-- TOC entry 4978 (class 2606 OID 38238)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (payment_id);


--
-- TOC entry 4980 (class 2606 OID 38240)
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- TOC entry 4982 (class 2606 OID 38242)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);


--
-- TOC entry 4984 (class 2606 OID 38244)
-- Name: school_migrations school_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.school_migrations
    ADD CONSTRAINT school_migrations_pkey PRIMARY KEY (migration_key);


--
-- TOC entry 4986 (class 2606 OID 38246)
-- Name: student_accounts student_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_accounts
    ADD CONSTRAINT student_accounts_pkey PRIMARY KEY (account_id);


--
-- TOC entry 4988 (class 2606 OID 38248)
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (student_id);


--
-- TOC entry 4990 (class 2606 OID 38250)
-- Name: weekly_schedule weekly_schedule_group_id_weekday_lesson_time_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule
    ADD CONSTRAINT weekly_schedule_group_id_weekday_lesson_time_key UNIQUE (group_id, weekday, lesson_time);


--
-- TOC entry 4992 (class 2606 OID 38252)
-- Name: weekly_schedule weekly_schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule
    ADD CONSTRAINT weekly_schedule_pkey PRIMARY KEY (schedule_id);


--
-- TOC entry 4993 (class 2606 OID 38253)
-- Name: attendance attendance_lesson_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_lesson_id_fkey FOREIGN KEY (lesson_id) REFERENCES public.lessons(lesson_id);


--
-- TOC entry 4994 (class 2606 OID 38258)
-- Name: attendance attendance_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(student_id);


--
-- TOC entry 4995 (class 2606 OID 38263)
-- Name: curators curators_discipline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curators
    ADD CONSTRAINT curators_discipline_id_fkey FOREIGN KEY (discipline_id) REFERENCES public.disciplines(discipline_id);


--
-- TOC entry 4996 (class 2606 OID 38268)
-- Name: curators curators_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curators
    ADD CONSTRAINT curators_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(employee_id);


--
-- TOC entry 4997 (class 2606 OID 38273)
-- Name: curators curators_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.curators
    ADD CONSTRAINT curators_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(group_id);


--
-- TOC entry 4998 (class 2606 OID 38278)
-- Name: disciplines disciplines_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disciplines
    ADD CONSTRAINT disciplines_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(employee_id);


--
-- TOC entry 4999 (class 2606 OID 38283)
-- Name: employees employees_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id);


--
-- TOC entry 5000 (class 2606 OID 38288)
-- Name: grades grades_discipline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_discipline_id_fkey FOREIGN KEY (discipline_id) REFERENCES public.disciplines(discipline_id);


--
-- TOC entry 5001 (class 2606 OID 38293)
-- Name: grades grades_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(student_id);


--
-- TOC entry 5002 (class 2606 OID 38298)
-- Name: groups groups_curator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_curator_id_fkey FOREIGN KEY (curator_id) REFERENCES public.employees(employee_id);


--
-- TOC entry 5003 (class 2606 OID 38303)
-- Name: groups groups_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(employee_id);


--
-- TOC entry 5004 (class 2606 OID 38308)
-- Name: lessons lessons_discipline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_discipline_id_fkey FOREIGN KEY (discipline_id) REFERENCES public.disciplines(discipline_id);


--
-- TOC entry 5005 (class 2606 OID 38313)
-- Name: lessons lessons_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(group_id);


--
-- TOC entry 5006 (class 2606 OID 38318)
-- Name: lessons lessons_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lessons
    ADD CONSTRAINT lessons_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(employee_id);


--
-- TOC entry 5007 (class 2606 OID 38323)
-- Name: payments payments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(student_id);


--
-- TOC entry 5008 (class 2606 OID 38328)
-- Name: student_accounts student_accounts_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.student_accounts
    ADD CONSTRAINT student_accounts_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(student_id);


--
-- TOC entry 5009 (class 2606 OID 38333)
-- Name: students students_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(group_id);


--
-- TOC entry 5010 (class 2606 OID 38338)
-- Name: weekly_schedule weekly_schedule_discipline_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule
    ADD CONSTRAINT weekly_schedule_discipline_id_fkey FOREIGN KEY (discipline_id) REFERENCES public.disciplines(discipline_id);


--
-- TOC entry 5011 (class 2606 OID 38343)
-- Name: weekly_schedule weekly_schedule_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule
    ADD CONSTRAINT weekly_schedule_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(group_id);


--
-- TOC entry 5012 (class 2606 OID 38348)
-- Name: weekly_schedule weekly_schedule_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.weekly_schedule
    ADD CONSTRAINT weekly_schedule_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.employees(employee_id);


-- Completed on 2026-10-31 19:43:02

--
-- PostgreSQL database dump complete
--

\unrestrict IgbTwTFln2QVBvXtat4CDFZUld1rK8kl4djVPCVDqeaW9xXkkG9zyaDK2AcFAd0

