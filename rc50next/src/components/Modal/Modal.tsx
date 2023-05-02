import React from "react";

import styles from './Modal.module.scss'


const Modal = ({ children, shown, close, title }: { children: any, shown: any, close: any, title: string }) => {

  return shown ? (
    <div
      className={styles.modalBackdrop}
      onClick={() => {
        close();
      }}
    >
      <div
        className={styles.modalContent}
        onClick={e => {
          e.stopPropagation();
        }}
      >
        <div className={styles.inner}>
          <button className={styles.closeButton} onClick={close}><span><span className="sr-only"></span></span></button>
          <div className={styles.modalHeading}>
            <h2>{title}</h2>
            {children}
          </div>
        </div>
      </div>
    </div>
  ) : null;
}

export default Modal;