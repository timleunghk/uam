export interface UploadFile_Permission {
    status: number;
    description: string;
    canEdit: boolean;
}
export interface UploadedFile {
    id?: number;
    file_name?: string;
    url?: string;
}
export interface UploadedFiles {
    [index: number]: UploadedFile[];
}
export interface MailTo {
    id?: string;
    to?: string[];
    cc?: string[];
    status?: number;
}

export interface AdGroup {
    id: string;
    name: string;
}
export interface LnGroup {
    id: string;
    name: string;
}
export interface SimpleCode {
    id: string;
    name: string;
    is_default: boolean;
}
export interface AdOU extends SimpleCode {
}
export interface AdOU extends SimpleCode {
}
export interface BaseRequest {
    id?: number;
    request_id?: string;
    creation_date?: Date;
    creation_user: string;
    last_modification_date?: Date;   
    last_modification_user: string;
    status: number;
    resourcetype: string;   
    review_by?: string[]; 
    copy_to?: string[]; 
    mail_to?: MailTo;
    update_mail_to?: MailTo;
    uploaded_files?: UploadedFiles;
    delete_files?: number[];
    read_only?: boolean;
    ad_user_groups?: AdGroup[];
    update_ad_user_groups?: AdGroup[];
    ln_user_groups?: LnGroup[];
    update_ln_user_groups?: LnGroup[];
    account_type?: number;
}

export interface AccountRequestBasicUserInfo {
    account_effective_start_date: Date;
    account_effective_end_date: Date;
    title: string;
    surname: string;
    given_name: string;
    surname_chinese: string;
    given_name_chinese: string;
    prefered_name: string;
}
export interface GenericAccountRequest extends BaseRequest, AccountRequestBasicUserInfo {
    oth_other_request: string;
    submission_date: Date;
}

export interface AccountRequestSysInfo {
    oa_need_windows_login: boolean;
    ad_windows_login_name: string;
    ad_account_expiry_date: Date;
    ad_ps_magistrate_of_lt: string[];
    oa_need_lotus_notes: boolean;
    ln_lotus_notes_mail_name: string;
}
export interface GenericAccountReview extends GenericAccountRequest, AccountRequestSysInfo {
    oth_other_justification: string;
}

export interface GenericAccountExecute extends GenericAccountReview {
    oth_other_remark: string;
}

export interface MailAddr {
    email: string;
}

export interface LoginUserInfo {
    username: string;
    permissions: string[];
    section: string;
}

export interface Section {
    id: number;
    code: string;
    description: string;
}

export interface Rank {
    id: number;
    value: string;
    description: string;
}

export interface AdName {
    ad_windows_login_name: string;
}

export interface RomaInfo {
    id: string;
    roma_id: string;
    roma_full_name: string;
    hkid: string;
}