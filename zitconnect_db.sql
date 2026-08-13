-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 13, 2026 at 04:31 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `zitconnect_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `administrator`
--

CREATE TABLE `administrator` (
  `adminID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `administrator`
--

INSERT INTO `administrator` (`adminID`) VALUES
(6);

-- --------------------------------------------------------

--
-- Table structure for table `availability`
--

CREATE TABLE `availability` (
  `availabilityID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `dayOfWeek` varchar(10) DEFAULT NULL,
  `timeSlot` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `availability`
--

INSERT INTO `availability` (`availabilityID`, `tutorID`, `dayOfWeek`, `timeSlot`) VALUES
(1, 5, 'Monday', '07:00-08:00'),
(2, 5, 'Monday', '08:00-09:00'),
(7, 5, 'Saturday', '16:00-17:00'),
(3, 5, 'Tuesday', '08:00-09:00'),
(4, 5, 'Tuesday', '09:00-10:00'),
(5, 5, 'Wednesday', '09:00-10:00'),
(6, 5, 'Wednesday', '16:00-17:00');

-- --------------------------------------------------------

--
-- Table structure for table `badge`
--

CREATE TABLE `badge` (
  `badgeID` int(11) NOT NULL,
  `badgeName` varchar(100) NOT NULL,
  `criteriaDescription` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `courseCode` varchar(15) NOT NULL,
  `courseName` varchar(150) NOT NULL,
  `schoolID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `course`
--

INSERT INTO `course` (`courseCode`, `courseName`, `schoolID`) VALUES
('CS120', 'Introduction to Computer Systems', 1),
('CS130', 'Introduction to Software Engineering', 1),
('CS150', 'Instroduction to Programming', 1),
('CS225', 'Operating Systems Concept', 1),
('CS230', 'Software Engineering', 1),
('CS235', 'Database Systems', 1),
('CS250', 'Object Oriented Programming', 1),
('CS270', 'Digital Design', 1),
('CS301', 'Project Management', 1),
('CS320', 'Data Communication and Networking', 1),
('CS345', 'Automata', 1),
('CS350', 'Object Oriented Programming with Java', 1),
('CS351', 'Numerical Analysis', 1),
('CS361', 'Web Programming', 1),
('LA111', 'Communication Skills', 1),
('MA110', 'Mathematical Methods', 1),
('MA210', 'Engineering Mathematics', 1),
('PH110', 'Introcution to Physics', 1),
('PH212', 'General Physics', 1);

-- --------------------------------------------------------

--
-- Table structure for table `groupsession`
--

CREATE TABLE `groupsession` (
  `groupSessionID` int(11) NOT NULL,
  `maxCapacity` int(11) DEFAULT NULL,
  `enrolledCount` int(11) DEFAULT 0,
  `pricePerStudent` decimal(10,2) DEFAULT NULL,
  `meetingPlatform` varchar(50) DEFAULT NULL,
  `accessLink` varchar(255) DEFAULT NULL,
  `accessLinkUnlocked` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `groupsession`
--

INSERT INTO `groupsession` (`groupSessionID`, `maxCapacity`, `enrolledCount`, `pricePerStudent`, `meetingPlatform`, `accessLink`, `accessLinkUnlocked`) VALUES
(12, 80, 0, 80.00, 'Zoom', 'https://lenco-api.readme.io/v2.0/reference/initiate-transfer-to-mobile-money', 0),
(13, 90, 1, 2.00, 'Zoom', 'https://lenco-api.readme.io/v2.0/reference/initiate-transfer-to-mobile-money', 1),
(15, 10, 1, 3.00, 'Zoom', 'https://claude.ai/chat/149fe543-fa0b-4ea5-a030-124cd121da5b', 1);

-- --------------------------------------------------------

--
-- Table structure for table `notification`
--

CREATE TABLE `notification` (
  `notificationID` int(11) NOT NULL,
  `userID` int(11) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `isRead` tinyint(1) DEFAULT 0,
  `createdAt` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification`
--

INSERT INTO `notification` (`notificationID`, `userID`, `message`, `isRead`, `createdAt`) VALUES
(1, 2, 'Your session for CS250 has been marked as completed. You can now rate the tutor.', 0, '2026-07-14 06:23:06'),
(2, 2, 'Your session for CS350 has been marked as completed. You can now rate the tutor.', 0, '2026-07-23 05:52:40'),
(3, 2, 'Your session request for CS250 has been accepted.', 0, '2026-07-23 06:35:28'),
(4, 12, 'Your session request for CS250 has been accepted.', 0, '2026-08-04 12:08:04'),
(5, 2, 'Your session request for CS250 has been declined.', 0, '2026-08-04 12:25:12'),
(6, 2, 'Your session request for CS250 has been accepted.', 0, '2026-08-04 12:34:30'),
(7, 2, 'Your session request for CS270 has been accepted.', 0, '2026-08-10 11:43:42'),
(8, 2, 'Your session for CS270 has been marked as completed. You can now rate the tutor.', 0, '2026-08-10 11:43:49'),
(9, 5, 'You earned K1.80 from a session payment.', 0, '2026-08-11 23:06:16'),
(10, 2, 'Your payment was successful! You can now join the session.', 0, '2026-08-11 23:06:16'),
(11, 5, 'You earned K2.70 from a session payment.', 0, '2026-08-12 06:56:33'),
(12, 2, 'Your payment was successful! You can now join the session.', 0, '2026-08-12 06:56:33');

-- --------------------------------------------------------

--
-- Table structure for table `payment`
--

CREATE TABLE `payment` (
  `paymentID` int(11) NOT NULL,
  `groupSessionID` int(11) DEFAULT NULL,
  `studentID` int(11) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `paymentStatus` enum('pending','successful','failed') DEFAULT 'pending',
  `transactionID` varchar(100) DEFAULT NULL,
  `paymentDate` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payment`
--

INSERT INTO `payment` (`paymentID`, `groupSessionID`, `studentID`, `amount`, `paymentStatus`, `transactionID`, `paymentDate`) VALUES
(32, 13, 2, 2.00, 'successful', 'ZIT-5B29EE59', NULL),
(33, 15, 2, 3.00, 'successful', 'ZIT-E48E1548', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `payout`
--

CREATE TABLE `payout` (
  `payoutID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payoutStatus` enum('pending','successful','failed') NOT NULL DEFAULT 'pending',
  `reference` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `operator` varchar(20) DEFAULT NULL,
  `reasonForFailure` varchar(255) DEFAULT NULL,
  `createdAt` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `program`
--

CREATE TABLE `program` (
  `programID` int(11) NOT NULL,
  `programName` varchar(150) NOT NULL,
  `schoolID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `program`
--

INSERT INTO `program` (`programID`, `programName`, `schoolID`) VALUES
(1, 'Bachelor of Science in Computer Science', 1),
(2, 'Bachelor of Science in Information Systems', 1),
(3, 'Bachelor of Science in Computer Engineering', 1),
(4, 'Bachelor of Science in ICT with Education', 1);

-- --------------------------------------------------------

--
-- Table structure for table `rating`
--

CREATE TABLE `rating` (
  `ratingID` int(11) NOT NULL,
  `sessionID` int(11) DEFAULT NULL,
  `studentID` int(11) DEFAULT NULL,
  `tutorID` int(11) DEFAULT NULL,
  `stars` int(11) DEFAULT NULL CHECK (`stars` between 1 and 5),
  `feedbackComment` text DEFAULT NULL,
  `createdAt` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rating`
--

INSERT INTO `rating` (`ratingID`, `sessionID`, `studentID`, `tutorID`, `stars`, `feedbackComment`, `createdAt`) VALUES
(1, NULL, 2, 5, 2, 'Well taught', '2026-07-14 06:27:25');

-- --------------------------------------------------------

--
-- Table structure for table `school`
--

CREATE TABLE `school` (
  `schoolID` int(11) NOT NULL,
  `schoolName` varchar(100) NOT NULL,
  `schoolCode` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `school`
--

INSERT INTO `school` (`schoolID`, `schoolName`, `schoolCode`) VALUES
(1, 'School of Information and Communication Technology', 'SICT');

-- --------------------------------------------------------

--
-- Table structure for table `session`
--

CREATE TABLE `session` (
  `sessionID` int(11) NOT NULL,
  `studentID` int(11) DEFAULT NULL,
  `tutorID` int(11) NOT NULL,
  `courseCode` varchar(15) NOT NULL,
  `sessionType` enum('individual','group') NOT NULL DEFAULT 'individual',
  `scheduledDate` date NOT NULL,
  `scheduledTime` time NOT NULL,
  `status` enum('pending','confirmed','declined','completed','cancelled') NOT NULL DEFAULT 'pending',
  `createdAt` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `session`
--

INSERT INTO `session` (`sessionID`, `studentID`, `tutorID`, `courseCode`, `sessionType`, `scheduledDate`, `scheduledTime`, `status`, `createdAt`) VALUES
(1, 2, 5, 'CS150', 'individual', '2026-06-25', '10:00:00', 'declined', '2026-06-05 19:35:09'),
(2, 2, 5, 'CS250', 'individual', '2026-08-17', '14:00:00', 'completed', '2026-06-07 19:25:30'),
(3, 8, 5, 'CS150', 'individual', '2026-06-18', '14:00:00', 'declined', '2026-06-17 13:20:02'),
(4, 2, 5, 'CS150', 'individual', '2026-06-23', '10:00:00', 'confirmed', '2026-06-22 13:18:11'),
(5, NULL, 5, 'CS150', 'group', '2026-07-28', '17:40:00', 'pending', '2026-07-12 06:47:38'),
(6, 2, 5, 'CS350', 'individual', '2026-08-18', '10:00:00', 'completed', '2026-07-12 07:59:54'),
(7, 2, 5, 'CS250', 'individual', '2026-07-27', '07:00:00', 'confirmed', '2026-07-23 06:13:10'),
(8, 12, 5, 'CS250', 'individual', '2026-08-05', '09:00:00', 'confirmed', '2026-08-04 12:04:58'),
(9, 2, 5, 'CS250', 'individual', '2026-08-11', '09:00:00', 'declined', '2026-08-04 12:23:36'),
(10, 2, 5, 'CS250', 'individual', '2026-08-05', '09:00:00', 'confirmed', '2026-08-04 12:33:42'),
(11, NULL, 5, 'CS270', 'group', '2026-08-10', '13:00:00', 'pending', '2026-08-10 02:29:55'),
(12, NULL, 5, 'CS270', 'group', '2026-08-13', '18:07:00', 'pending', '2026-08-10 11:15:33'),
(13, NULL, 5, 'CS270', 'group', '2026-08-12', '21:08:00', 'pending', '2026-08-10 11:16:05'),
(14, 2, 5, 'CS270', 'individual', '2026-08-10', '08:00:00', 'completed', '2026-08-10 11:43:27'),
(15, NULL, 5, 'CS250', 'group', '2026-08-13', '21:09:00', 'pending', '2026-08-12 06:55:32');

-- --------------------------------------------------------

--
-- Table structure for table `student`
--

CREATE TABLE `student` (
  `studentID` int(11) NOT NULL,
  `programID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `student`
--

INSERT INTO `student` (`studentID`, `programID`) VALUES
(2, 1),
(8, 1),
(11, 1),
(12, 1),
(10, 4);

-- --------------------------------------------------------

--
-- Table structure for table `tutor`
--

CREATE TABLE `tutor` (
  `tutorID` int(11) NOT NULL,
  `verificationStatus` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending',
  `averageRating` decimal(3,2) NOT NULL DEFAULT 0.00,
  `bio` varchar(500) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tutor`
--

INSERT INTO `tutor` (`tutorID`, `verificationStatus`, `averageRating`, `bio`) VALUES
(5, 'approved', 2.00, 'I am an expert at Computer Programming with 10 years experience'),
(7, 'approved', 0.00, ''),
(9, 'rejected', 0.00, ''),
(13, 'pending', 0.00, '');

-- --------------------------------------------------------

--
-- Table structure for table `tutorbadge`
--

CREATE TABLE `tutorbadge` (
  `tutorBadgeID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `badgeID` int(11) NOT NULL,
  `dateAwarded` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tutorcourse`
--

CREATE TABLE `tutorcourse` (
  `tutorCourseID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `courseCode` varchar(15) NOT NULL,
  `gradeObtained` varchar(5) NOT NULL,
  `pricePerSession` decimal(10,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tutorcourse`
--

INSERT INTO `tutorcourse` (`tutorCourseID`, `tutorID`, `courseCode`, `gradeObtained`, `pricePerSession`) VALUES
(2, 5, 'CS250', 'pendi', 50.00),
(3, 5, 'CS350', 'pendi', 0.00),
(4, 7, 'CS120', 'pendi', 0.00),
(5, 7, 'CS130', 'pendi', 0.00),
(6, 7, 'CS235', 'pendi', 0.00),
(7, 9, 'CS120', 'pendi', 0.00),
(8, 9, 'CS130', 'pendi', 0.00),
(9, 9, 'CS230', 'pendi', 0.00),
(10, 9, 'PH110', 'pendi', 0.00),
(11, 5, 'CS270', 'pendi', 1.00),
(12, 13, 'CS130', 'pendi', 0.00),
(13, 13, 'CS350', 'pendi', 0.00),
(14, 13, 'PH110', 'pendi', 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `userID` int(11) NOT NULL,
  `fullName` varchar(100) NOT NULL,
  `userName` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('student','tutor','admin') NOT NULL,
  `profilePicture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`userID`, `fullName`, `userName`, `email`, `password`, `role`, `profilePicture`) VALUES
(2, 'Newton Katete', 'newtonisaackatete@gmail.com', 'newtonisaackatete@gmail.com', '12345678', 'student', 'uploads/profile_pics/profile_2_unidata.png'),
(5, 'Albert Kangombe', 'kangombe', 'kangombe@gmail.com', '12345678', 'tutor', 'uploads/profile_pics/profile_5_team.png'),
(6, 'Suwilanji Sinkamba', 'suwi', 'suwi@gmail.com', '12345678', 'admin', NULL),
(7, 'Fred', 'Man', 'fredman@gmail.com', '12345678', 'tutor', NULL),
(8, 'Cecilia Mwape', 'ceclia1234', 'ceclia@gmail.com', '12345678', 'student', NULL),
(9, 'Henry', 'chali', 'pm@gmail.com', '1234567', 'tutor', NULL),
(10, 'LUNGU BERTHA', 'lungu', 'bertha@gmail.com', '12345678', 'student', NULL),
(11, 'Richard Chipasha', 'Chipasha', 'rc@gmail.com', '12345678', 'student', NULL),
(12, 'Henry PM Chali', 'henrychali', 'hpmc@gmail.com', '12345678', 'student', NULL),
(13, 'Cecilia Mwape', 'mwape', 'mwape@gmail.com', 'Cecilia1234', 'tutor', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `verificationdocument`
--

CREATE TABLE `verificationdocument` (
  `documentID` int(11) NOT NULL,
  `tutorID` int(11) NOT NULL,
  `documentType` enum('result_slip','transcript') NOT NULL,
  `filePath` varchar(255) NOT NULL,
  `uploadDate` datetime NOT NULL DEFAULT current_timestamp(),
  `approvalStatus` enum('pending','approved','rejected') NOT NULL DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `verificationdocument`
--

INSERT INTO `verificationdocument` (`documentID`, `tutorID`, `documentType`, `filePath`, `uploadDate`, `approvalStatus`) VALUES
(1, 5, 'result_slip', 'uploads/The_Signal_Through_the_Noise.pdf', '2026-05-31 14:12:47', 'approved'),
(2, 13, 'result_slip', 'uploads/The_HTML5_Architect_1786587452.pdf', '2026-08-12 22:17:33', 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `wallet`
--

CREATE TABLE `wallet` (
  `walletID` int(11) NOT NULL,
  `tutorID` int(11) DEFAULT NULL,
  `availableBalance` decimal(10,2) DEFAULT 0.00,
  `totalWithdrawn` decimal(10,2) DEFAULT 0.00,
  `payoutPhone` varchar(20) DEFAULT NULL,
  `payoutOperator` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wallet`
--

INSERT INTO `wallet` (`walletID`, `tutorID`, `availableBalance`, `totalWithdrawn`, `payoutPhone`, `payoutOperator`) VALUES
(1, 5, 4.50, 0.00, NULL, NULL),
(4, 13, 0.00, 0.00, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `administrator`
--
ALTER TABLE `administrator`
  ADD PRIMARY KEY (`adminID`);

--
-- Indexes for table `availability`
--
ALTER TABLE `availability`
  ADD PRIMARY KEY (`availabilityID`),
  ADD UNIQUE KEY `tutorID` (`tutorID`,`dayOfWeek`,`timeSlot`);

--
-- Indexes for table `badge`
--
ALTER TABLE `badge`
  ADD PRIMARY KEY (`badgeID`);

--
-- Indexes for table `course`
--
ALTER TABLE `course`
  ADD PRIMARY KEY (`courseCode`),
  ADD KEY `fk_course_school` (`schoolID`);

--
-- Indexes for table `groupsession`
--
ALTER TABLE `groupsession`
  ADD PRIMARY KEY (`groupSessionID`);

--
-- Indexes for table `notification`
--
ALTER TABLE `notification`
  ADD PRIMARY KEY (`notificationID`);

--
-- Indexes for table `payment`
--
ALTER TABLE `payment`
  ADD PRIMARY KEY (`paymentID`),
  ADD KEY `groupSessionID` (`groupSessionID`),
  ADD KEY `studentID` (`studentID`);

--
-- Indexes for table `payout`
--
ALTER TABLE `payout`
  ADD PRIMARY KEY (`payoutID`),
  ADD UNIQUE KEY `reference` (`reference`),
  ADD KEY `tutorID` (`tutorID`);

--
-- Indexes for table `program`
--
ALTER TABLE `program`
  ADD PRIMARY KEY (`programID`),
  ADD KEY `fk_program_school` (`schoolID`);

--
-- Indexes for table `rating`
--
ALTER TABLE `rating`
  ADD PRIMARY KEY (`ratingID`),
  ADD KEY `sessionID` (`sessionID`);

--
-- Indexes for table `school`
--
ALTER TABLE `school`
  ADD PRIMARY KEY (`schoolID`),
  ADD UNIQUE KEY `uq_schoolCode` (`schoolCode`);

--
-- Indexes for table `session`
--
ALTER TABLE `session`
  ADD PRIMARY KEY (`sessionID`),
  ADD KEY `fk_session_student` (`studentID`),
  ADD KEY `fk_session_tutor` (`tutorID`),
  ADD KEY `fk_session_course` (`courseCode`);

--
-- Indexes for table `student`
--
ALTER TABLE `student`
  ADD PRIMARY KEY (`studentID`),
  ADD KEY `fk_student_program` (`programID`);

--
-- Indexes for table `tutor`
--
ALTER TABLE `tutor`
  ADD PRIMARY KEY (`tutorID`);

--
-- Indexes for table `tutorbadge`
--
ALTER TABLE `tutorbadge`
  ADD PRIMARY KEY (`tutorBadgeID`),
  ADD UNIQUE KEY `uq_tutor_badge` (`tutorID`,`badgeID`),
  ADD KEY `fk_tutorbadge_badge` (`badgeID`);

--
-- Indexes for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  ADD PRIMARY KEY (`tutorCourseID`),
  ADD UNIQUE KEY `uq_tutor_course` (`tutorID`,`courseCode`),
  ADD KEY `fk_tutorcourse_course` (`courseCode`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`userID`),
  ADD UNIQUE KEY `userName` (`userName`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  ADD PRIMARY KEY (`documentID`),
  ADD KEY `fk_verdoc_tutor` (`tutorID`);

--
-- Indexes for table `wallet`
--
ALTER TABLE `wallet`
  ADD PRIMARY KEY (`walletID`),
  ADD UNIQUE KEY `tutorID` (`tutorID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `availability`
--
ALTER TABLE `availability`
  MODIFY `availabilityID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `badge`
--
ALTER TABLE `badge`
  MODIFY `badgeID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notification`
--
ALTER TABLE `notification`
  MODIFY `notificationID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `payment`
--
ALTER TABLE `payment`
  MODIFY `paymentID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT for table `payout`
--
ALTER TABLE `payout`
  MODIFY `payoutID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `program`
--
ALTER TABLE `program`
  MODIFY `programID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `rating`
--
ALTER TABLE `rating`
  MODIFY `ratingID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `school`
--
ALTER TABLE `school`
  MODIFY `schoolID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `session`
--
ALTER TABLE `session`
  MODIFY `sessionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `tutorbadge`
--
ALTER TABLE `tutorbadge`
  MODIFY `tutorBadgeID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  MODIFY `tutorCourseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `userID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  MODIFY `documentID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `wallet`
--
ALTER TABLE `wallet`
  MODIFY `walletID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `administrator`
--
ALTER TABLE `administrator`
  ADD CONSTRAINT `fk_administrator_user` FOREIGN KEY (`adminID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `availability`
--
ALTER TABLE `availability`
  ADD CONSTRAINT `availability_ibfk_1` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `course`
--
ALTER TABLE `course`
  ADD CONSTRAINT `fk_course_school` FOREIGN KEY (`schoolID`) REFERENCES `school` (`schoolID`);

--
-- Constraints for table `groupsession`
--
ALTER TABLE `groupsession`
  ADD CONSTRAINT `groupsession_ibfk_1` FOREIGN KEY (`groupSessionID`) REFERENCES `session` (`sessionID`);

--
-- Constraints for table `payment`
--
ALTER TABLE `payment`
  ADD CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`groupSessionID`) REFERENCES `groupsession` (`groupSessionID`),
  ADD CONSTRAINT `payment_ibfk_2` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`);

--
-- Constraints for table `payout`
--
ALTER TABLE `payout`
  ADD CONSTRAINT `payout_ibfk_1` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `program`
--
ALTER TABLE `program`
  ADD CONSTRAINT `fk_program_school` FOREIGN KEY (`schoolID`) REFERENCES `school` (`schoolID`);

--
-- Constraints for table `rating`
--
ALTER TABLE `rating`
  ADD CONSTRAINT `rating_ibfk_1` FOREIGN KEY (`sessionID`) REFERENCES `session` (`sessionID`);

--
-- Constraints for table `session`
--
ALTER TABLE `session`
  ADD CONSTRAINT `fk_session_course` FOREIGN KEY (`courseCode`) REFERENCES `course` (`courseCode`),
  ADD CONSTRAINT `fk_session_student` FOREIGN KEY (`studentID`) REFERENCES `student` (`studentID`),
  ADD CONSTRAINT `fk_session_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `student`
--
ALTER TABLE `student`
  ADD CONSTRAINT `fk_student_program` FOREIGN KEY (`programID`) REFERENCES `program` (`programID`),
  ADD CONSTRAINT `fk_student_user` FOREIGN KEY (`studentID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `tutor`
--
ALTER TABLE `tutor`
  ADD CONSTRAINT `fk_tutor_user` FOREIGN KEY (`tutorID`) REFERENCES `user` (`userID`);

--
-- Constraints for table `tutorbadge`
--
ALTER TABLE `tutorbadge`
  ADD CONSTRAINT `fk_tutorbadge_badge` FOREIGN KEY (`badgeID`) REFERENCES `badge` (`badgeID`),
  ADD CONSTRAINT `fk_tutorbadge_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `tutorcourse`
--
ALTER TABLE `tutorcourse`
  ADD CONSTRAINT `fk_tutorcourse_course` FOREIGN KEY (`courseCode`) REFERENCES `course` (`courseCode`),
  ADD CONSTRAINT `fk_tutorcourse_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `verificationdocument`
--
ALTER TABLE `verificationdocument`
  ADD CONSTRAINT `fk_verdoc_tutor` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);

--
-- Constraints for table `wallet`
--
ALTER TABLE `wallet`
  ADD CONSTRAINT `wallet_ibfk_1` FOREIGN KEY (`tutorID`) REFERENCES `tutor` (`tutorID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
